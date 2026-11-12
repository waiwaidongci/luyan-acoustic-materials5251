from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.study import StudyInput,StudyOut
from src.controllers import study_controller as controller
router=APIRouter(prefix='/studies',tags=['studies'])
@router.get('',response_model=list[StudyOut])
def index(db=Depends(get_db),user=Depends(current_user)):return controller.index(db)
@router.post('',response_model=StudyOut,status_code=201)
def create(data:StudyInput,db=Depends(get_db),user=Depends(editor)):return controller.create(db,data)
@router.put('/{id}',response_model=StudyOut)
def update(id:int,data:StudyInput,db=Depends(get_db),user=Depends(editor)):return controller.update(db,id,data)
