import json
from pathlib import Path
from sqlalchemy import select,func
from sqlalchemy.orm import defer
from fastapi import HTTPException
from redis import Redis
from src.config.settings import REDIS_URL,ARTIFACTS_DIR
from src.models import DecisionRun,MaterialSample
from src.services.study_service import get_study
from src.services.criterion_service import list_criteria
from src.services.weight_sensitivity import analyze_decision
from src.services import staleness_service
redis=Redis.from_url(REDIS_URL)
ACTIVE=('queued','running')
def list_runs(db):return db.scalars(select(DecisionRun).options(defer(DecisionRun.result),defer(DecisionRun.snapshot)).order_by(DecisionRun.id.desc())).all()
def get_run(db,id):
    item=db.get(DecisionRun,id)
    if not item:raise HTTPException(404,'权衡任务不存在')
    return item

def _active_count(db):
    return db.scalar(select(func.count()).select_from(DecisionRun).where(DecisionRun.status.in_(list(ACTIVE))))

def _build_snapshot(db,study):
    criteria=[{k:getattr(c,k) for k in ('id','code','name','unit','direction','center_weight')} for c in list_criteria(db,study.id)]
    fields=('id','code','name','family','absorption','impact','carbon','price','thickness','batch')
    samples=[{k:getattr(s,k) for k in fields} for s in db.scalars(select(MaterialSample).where(MaterialSample.id.in_(study.material_ids)).order_by(MaterialSample.code)).all()]
    snapshot={'study':{'id':study.id,'code':study.code,'name':study.name,'source_file':study.source_file,'material_ids':study.material_ids},'samples':samples,'criteria':criteria}
    return snapshot,criteria,samples

def create_run(db,data):
    study=get_study(db,data.study_id)
    if db.scalar(select(DecisionRun).where(DecisionRun.name==data.name)):raise HTTPException(409,'任务名称已存在')
    if _active_count(db)>=3:raise HTTPException(429,'已有3项活动任务，请等待完成')
    criteria=[{k:getattr(c,k) for k in ('id','code','name','unit','direction','center_weight')} for c in list_criteria(db,study.id)]
    weights=data.center_weights or {c['code']:c['center_weight'] for c in criteria}
    if set(weights)!={c['code'] for c in criteria}:raise HTTPException(422,'中心权重须逐一覆盖本研究指标')
    snapshot,_,samples=_build_snapshot(db,study)
    signature=staleness_service.current_source(db,study)
    item=DecisionRun(**{**data.model_dump(),'center_weights':weights},snapshot=snapshot,
        summary={'samples':len(samples),'criteria':len(criteria)},status='queued',
        source_fingerprint=staleness_service.fingerprint_payload(signature),source_signature=signature,
        recalc_of_id=None,recalc_seq=0,recalc_status='')
    db.add(item);db.commit()
    try:redis.lpush('material:runs',str(item.id))
    except Exception:pass
    return item

def _latest_in_chain(db,root_id):
    """Most recent recalculation of root_id, or the root itself when no recalc exists."""
    descendants=db.scalars(select(DecisionRun).where(DecisionRun.recalc_of_id==root_id).order_by(DecisionRun.recalc_seq.desc(),DecisionRun.id.desc())).all()
    return descendants[0] if descendants else db.get(DecisionRun,root_id)

def recalculate_run(db,id):
    """Recalculate one trade-off with its original preferences.

    Always operates on the chain head. Repeating a revision that already produced a
    current result is a no-op returning that result, so no duplicate task is ever created.
    """
    get_run(db,id)
    root_id=id
    direct=db.get(DecisionRun,id)
    if direct.recalc_of_id:
        root_id=direct.recalc_of_id
    root=db.get(DecisionRun,root_id)
    latest=_latest_in_chain(db,root_id)
    if latest.status in ACTIVE:
        raise HTTPException(409,'该任务的重算正在进行，请勿重复提交')
    # Idempotency: a completed head whose source is current is the answer for any revision seen so far.
    if latest.status=='completed' and not staleness_service.staleness_report(db,latest)['stale']:
        if latest.id==root_id and root_id==id:
            raise HTTPException(409,'源数据未变化，该权衡无需重算')
        return latest
    # A failed recalculation is retried in place instead of spawning another task row.
    if latest.id!=root_id and latest.status=='failed' and latest.recalc_status=='failed':
        return _queue_recalc(db,root,latest)
    if latest.id==root_id:
        if root.status!='completed':
            raise HTTPException(409,'仅已完成的权衡可进入重算流程')
        if not staleness_service.staleness_report(db,root)['stale']:
            raise HTTPException(409,'源数据未变化，该权衡无需重算')
    return _queue_recalc(db,root,latest)

def retry_recalc(db,id):
    run=db.get(DecisionRun,id)
    if not run or not (run.recalc_of_id and run.status=='failed' and run.recalc_status=='failed'):
        raise HTTPException(409,'仅失败的重算任务可以在原任务上重试')
    root=db.get(DecisionRun,run.recalc_of_id)
    latest=_latest_in_chain(db,root.id)
    if latest.id!=run.id:
        raise HTTPException(409,f'已有更新的重算版本 #{latest.id}，请基于最新版本操作')
    return _queue_recalc(db,root,latest)

def _queue_recalc(db,root,predecessor):
    """Create (or reset in place on retry) a recalculation run carrying the original preferences."""
    study=get_study(db,root.study_id)
    if _active_count(db)>=3:raise HTTPException(429,'已有3项活动任务，请等待完成后再重算')
    snapshot,criteria,samples=_build_snapshot(db,study)
    signature=staleness_service.current_source(db,study)
    seq=predecessor.recalc_seq+1
    retry = predecessor.recalc_of_id==root.id and predecessor.status=='failed' and predecessor.recalc_status=='failed'
    if retry:
        # Retry reuses the same failed task row: repeating a revision never adds a new task.
        item=predecessor
        item.snapshot=snapshot;item.source_signature=signature
        item.source_fingerprint=staleness_service.fingerprint_payload(signature)
        item.summary={'samples':len(samples),'criteria':len(criteria),'recalc_of':root.id,'recalc_seq':item.recalc_seq}
        item.error='';item.status='queued';item.recalc_status='queued';item.result={}
    else:
        base_name=root.name
        name=f'{base_name} · 数据重算 v{seq}'
        if len(name)>140:name=name[:140]
        suffix=1
        while db.scalar(select(DecisionRun).where(DecisionRun.name==name)):
            tail=f' · {suffix}';name=f'{base_name} · 数据重算 v{seq}{tail}'[:140];suffix+=1
        item=DecisionRun(name=name,study_id=root.study_id,center_weights=dict(root.center_weights),
            concentration=root.concentration,repeats=root.repeats,seed=root.seed,snapshot=snapshot,
            summary={'samples':len(samples),'criteria':len(criteria),'recalc_of':root.id,'recalc_seq':seq},
            status='queued',source_fingerprint=staleness_service.fingerprint_payload(signature),
            source_signature=signature,recalc_of_id=root.id,recalc_seq=seq,recalc_status='queued',error='')
        db.add(item)
    db.commit()
    try:redis.lpush('material:runs',str(item.id))
    except Exception:pass
    return item

def list_stale(db,study_id=None):
    """Staleness annotations for every completed/failed run, newest source state included."""
    rows=db.scalars(select(DecisionRun).options(defer(DecisionRun.result),defer(DecisionRun.snapshot)).order_by(DecisionRun.id.desc())).all()
    reports=[]
    for run in rows:
        if study_id and run.study_id!=study_id:continue
        if run.status not in ('completed','failed'):continue
        report=staleness_service.staleness_report(db,run)
        reports.append({'run_id':run.id,'name':run.name,'study_id':run.study_id,'status':run.status,
            'created_at':run.created_at,'recalc_of_id':run.recalc_of_id,'recalc_seq':run.recalc_seq,
            'recalc_status':run.recalc_status,**report})
    return reports

def recalculate_stale(db,study_id=None):
    """Batch recalculation with original preferences. Repeated calls never duplicate work."""
    created,skipped,already=[],[],[]
    rows=db.scalars(select(DecisionRun).order_by(DecisionRun.id)).all()
    for run in rows:
        if study_id and run.study_id!=study_id:continue
        if run.recalc_of_id is not None:continue  # descendants are handled via their chain root
        if run.status!='completed':continue
        report=staleness_service.staleness_report(db,run)
        if not report['stale']:continue
        latest=_latest_in_chain(db,run.id)
        if latest.status in ACTIVE:
            skipped.append({'run_id':run.id,'reason':'重算进行中','recalc_id':latest.id});continue
        if latest.recalc_of_id==run.id and latest.status=='completed' and not staleness_service.staleness_report(db,latest)['stale']:
            already.append({'run_id':run.id,'recalc_id':latest.id});continue
        try:
            item=_queue_recalc(db,run,latest)
            created.append({'run_id':run.id,'recalc_id':item.id,'recalc_seq':item.recalc_seq})
        except HTTPException as exc:
            db.rollback()
            skipped.append({'run_id':run.id,'reason':str(exc.detail)})
    return {'queued':created,'skipped':skipped,'up_to_date':already}

def execute_run(db,id):
    item=get_run(db,id)
    if item.status not in ('queued','running'):return
    item.status='running'
    if item.recalc_of_id:item.recalc_status='running'
    db.commit()
    try:
        result=analyze_decision(item.snapshot,item.center_weights,item.concentration,item.repeats,item.seed,lambda:Path('/tmp/heartbeat').touch())
        Path(ARTIFACTS_DIR).mkdir(exist_ok=True);Path(f'{ARTIFACTS_DIR}/run-{id}.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False))
        item.result=result
        summary={'samples':len(result['samples']),'criteria':len(result['criteria']),'all_indistinguishable':result['all_indistinguishable'],'fingerprint':result['fingerprint']}
        if item.recalc_of_id:summary.update({'recalc_of':item.recalc_of_id,'recalc_seq':item.recalc_seq})
        item.summary=summary;item.error='';item.status='completed'
        if item.recalc_of_id:item.recalc_status='completed'
        db.commit()
    except Exception as exc:
        db.rollback();item=get_run(db,id);item.status='failed';item.error=str(exc)[:600]
        if item.recalc_of_id:item.recalc_status='failed'
        db.commit()
