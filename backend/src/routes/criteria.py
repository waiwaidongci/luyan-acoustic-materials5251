from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.criterion import CriterionInput,CriterionOut
from src.controllers import criterion_controller as controller
router=APIRouter(prefix='/criteria',tags=['criteria'])
@router.get('',response_model=list[CriterionOut])
def index(study_id:int,db=Depends(get_db),user=Depends(current_user)):return controller.index(db,study_id)
@router.post('',response_model=CriterionOut,status_code=201)
def create(data:CriterionInput,db=Depends(get_db),user=Depends(editor)):return controller.create(db,data)
@router.put('/{id}',response_model=CriterionOut)
def update(id:int,data:CriterionInput,db=Depends(get_db),user=Depends(editor)):return controller.update(db,id,data)
