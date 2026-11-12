from sqlalchemy import select
from fastapi import HTTPException
from src.models import Criterion
from src.services.study_service import get_study

def list_criteria(db,study_id):return db.scalars(select(Criterion).where(Criterion.study_id==study_id).order_by(Criterion.code)).all()
def validate(db,data,id=None):
    get_study(db,data.study_id)
    if db.scalar(select(Criterion).where(Criterion.study_id==data.study_id,Criterion.code==data.code,Criterion.id!=(id or 0))):raise HTTPException(409,'研究已有该指标')
def create_criterion(db,data):
    validate(db,data);item=Criterion(**data.model_dump());db.add(item);db.commit();return item

def update_criterion(db,id,data):
    item=db.get(Criterion,id)
    if not item:raise HTTPException(404,'指标不存在')
    if item.study_id!=data.study_id:raise HTTPException(422,'不能迁移指标所属研究')
    validate(db,data,id)
    for k,v in data.model_dump().items():setattr(item,k,v)
    db.commit();return item
