from sqlalchemy import select
from fastapi import HTTPException
from src.models import CandidateStudy,MaterialSample

def list_studies(db):return db.scalars(select(CandidateStudy).order_by(CandidateStudy.id)).all()
def get_study(db,id):
    item=db.get(CandidateStudy,id)
    if not item:raise HTTPException(404,'权衡研究不存在')
    return item

def validate(db,data,id=None):
    if db.scalar(select(CandidateStudy).where(CandidateStudy.code==data.code,CandidateStudy.id!=(id or 0))):raise HTTPException(409,'研究编号已存在')
    if len(set(data.material_ids))!=len(data.material_ids):raise HTTPException(422,'候选试样重复')
    found=set(db.scalars(select(MaterialSample.id).where(MaterialSample.id.in_(data.material_ids))).all())
    if found!=set(data.material_ids):raise HTTPException(422,'候选包含不存在的试样')
def create_study(db,data):
    validate(db,data);item=CandidateStudy(**data.model_dump());db.add(item);db.commit();return item

def update_study(db,id,data):
    item=get_study(db,id);validate(db,data,id)
    for k,v in data.model_dump().items():setattr(item,k,v)
    db.commit();return item
