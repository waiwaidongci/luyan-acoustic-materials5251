from sqlalchemy import select,func
from fastapi import HTTPException
from src.models import MaterialSample

def list_samples(db):return db.scalars(select(MaterialSample).order_by(MaterialSample.code)).all()
def validate(db,data,id=None):
    if db.scalar(select(MaterialSample).where(MaterialSample.code==data.code,MaterialSample.id!=(id or 0))):raise HTTPException(409,'试样编号已存在')
def create_sample(db,data):
    validate(db,data)
    if db.scalar(select(func.count()).select_from(MaterialSample))>=300:raise HTTPException(422,'资料库最多300份试样')
    item=MaterialSample(**data.model_dump());db.add(item);db.commit();return item

def update_sample(db,id,data):
    item=db.get(MaterialSample,id)
    if not item:raise HTTPException(404,'试样不存在')
    validate(db,data,id)
    for k,v in data.model_dump().items():setattr(item,k,v)
    db.commit();return item
