import csv,io,json
from sqlalchemy import select
from fastapi import HTTPException
from src.models import TrialNote
from src.services.run_service import get_run

def list_notes(db):return db.scalars(select(TrialNote).order_by(TrialNote.id.desc())).all()
def create_note(db,data):
    run=get_run(db,data.run_id)
    if run.status!='completed':raise HTTPException(409,'只有完成的权衡研究可作为试样计划依据')
    if data.sample_id not in {s['id'] for s in run.result['samples']}:raise HTTPException(422,'试样须属于本次候选快照')
    if db.scalar(select(TrialNote).where(TrialNote.name==data.name)):raise HTTPException(409,'试样计划名称已存在')
    item=TrialNote(**data.model_dump());db.add(item);db.commit();return item

def review_note(db,id,data,user):
    item=db.get(TrialNote,id)
    if not item:raise HTTPException(404,'试样计划不存在')
    if item.status!='draft':raise HTTPException(409,'审阅决定不可覆盖，请另建修订计划')
    if data.status not in ('approved','rejected'):raise HTTPException(422,'请选择同意或退回')
    item.status=data.status;item.reviewer_note=data.reviewer_note;item.reviewed_by=user.email;db.commit();return item

def export_note(db,id):
    item=db.get(TrialNote,id)
    if not item:raise HTTPException(404,'试样计划不存在')
    if item.status!='approved':raise HTTPException(409,'仅已同意的试样计划可分发')
    run=get_run(db,item.run_id);r=run.result;out=io.StringIO();w=csv.writer(out)
    w.writerow(['note','sample_id','reviewer','reviewer_note','protocol','fingerprint','scope']);w.writerow([item.name,item.sample_id,item.reviewed_by,item.reviewer_note,item.protocol,r['fingerprint'],'偏好权重敏感性；不是统计置信、后验或采购建议'])
    w.writerow(['criterion','direction','unit','normalized_center_weight','alpha'])
    for c,weight,alpha in zip(r['criteria'],r['center_weights'],r['alpha']):w.writerow([c['code'],c['direction'],c['unit'],weight,alpha])
    w.writerow(['code','name','closeness','average_rank','scenario_best_rank','scenario_worst_rank','rank_q025','rank_q975','first_share','rank_frequency'])
    for s in r['samples']:w.writerow([s['code'],s['name'],s['score'],s['rank'],s['rank_min'],s['rank_max'],s['rank_low'],s['rank_high'],s['first_share'],json.dumps(s['rank_frequency'])])
    return '\ufeff'+out.getvalue()
