import json
from pathlib import Path
from sqlalchemy import select,func
from sqlalchemy.orm import defer
from fastapi import HTTPException
from redis import Redis
from src.config.settings import REDIS_URL
from src.models import DecisionRun,MaterialSample
from src.services.study_service import get_study
from src.services.criterion_service import list_criteria
from src.services.weight_sensitivity import analyze_decision
redis=Redis.from_url(REDIS_URL)
def list_runs(db):return db.scalars(select(DecisionRun).options(defer(DecisionRun.result),defer(DecisionRun.snapshot)).order_by(DecisionRun.id.desc())).all()
def get_run(db,id):
    item=db.get(DecisionRun,id)
    if not item:raise HTTPException(404,'权衡任务不存在')
    return item

def create_run(db,data):
    study=get_study(db,data.study_id)
    if db.scalar(select(DecisionRun).where(DecisionRun.name==data.name)):raise HTTPException(409,'任务名称已存在')
    if db.scalar(select(func.count()).select_from(DecisionRun).where(DecisionRun.status.in_(['queued','running'])))>=3:raise HTTPException(429,'已有3项活动任务，请等待完成')
    criteria=[{k:getattr(c,k) for k in ('id','code','name','unit','direction','center_weight')} for c in list_criteria(db,study.id)]
    weights=data.center_weights or {c['code']:c['center_weight'] for c in criteria}
    if set(weights)!={c['code'] for c in criteria}:raise HTTPException(422,'中心权重须逐一覆盖本研究指标')
    fields=('id','code','name','family','absorption','impact','carbon','price','thickness','batch')
    samples=[{k:getattr(s,k) for k in fields} for s in db.scalars(select(MaterialSample).where(MaterialSample.id.in_(study.material_ids)).order_by(MaterialSample.code)).all()]
    snapshot={'study':{'id':study.id,'code':study.code,'name':study.name,'source_file':study.source_file,'material_ids':study.material_ids},'samples':samples,'criteria':criteria}
    item=DecisionRun(**{**data.model_dump(),'center_weights':weights},snapshot=snapshot,summary={'samples':len(samples),'criteria':len(criteria)},status='queued');db.add(item);db.commit()
    try:redis.lpush('material:runs',str(item.id))
    except Exception:pass
    return item

def execute_run(db,id):
    item=get_run(db,id)
    if item.status not in ('queued','running'):return
    item.status='running';db.commit()
    try:
        result=analyze_decision(item.snapshot,item.center_weights,item.concentration,item.repeats,item.seed,lambda:Path('/tmp/heartbeat').touch())
        Path('/artifacts').mkdir(exist_ok=True);Path(f'/artifacts/run-{id}.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False))
        item.result=result;item.summary={'samples':len(result['samples']),'criteria':len(result['criteria']),'all_indistinguishable':result['all_indistinguishable'],'fingerprint':result['fingerprint']};item.error='';item.status='completed';db.commit()
    except Exception as exc:
        db.rollback();item=get_run(db,id);item.status='failed';item.error=str(exc)[:600];db.commit()
