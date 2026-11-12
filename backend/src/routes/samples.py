from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.sample import SampleInput,SampleOut
from src.controllers import sample_controller as controller
router=APIRouter(prefix='/samples',tags=['samples'])
@router.get('',response_model=list[SampleOut])
def index(db=Depends(get_db),user=Depends(current_user)):return controller.index(db)
@router.post('',response_model=SampleOut,status_code=201)
def create(data:SampleInput,db=Depends(get_db),user=Depends(editor)):return controller.create(db,data)
@router.put('/{id}',response_model=SampleOut)
def update(id:int,data:SampleInput,db=Depends(get_db),user=Depends(editor)):return controller.update(db,id,data)
