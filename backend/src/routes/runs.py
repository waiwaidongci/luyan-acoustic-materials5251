from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.run import RunInput,RunOut,RunSummary,StaleReport,RecalcResult,BatchRecalcInput
from src.controllers import run_controller as controller
router=APIRouter(prefix='/runs',tags=['runs'])
@router.get('',response_model=list[RunSummary])
def index(db=Depends(get_db),user=Depends(current_user)):return controller.index(db)
@router.post('',response_model=RunOut,status_code=201)
def create(data:RunInput,db=Depends(get_db),user=Depends(editor)):return controller.create(db,data)
@router.get('/stale',response_model=list[StaleReport])
def stale(study_id:int|None=None,db=Depends(get_db),user=Depends(current_user)):return controller.stale(db,study_id)
@router.post('/recalculate',response_model=RecalcResult)
def batch_recalc(data:BatchRecalcInput,db=Depends(get_db),user=Depends(editor)):return controller.batch_recalc(db,data)
@router.get('/{id}',response_model=RunOut)
def detail(id:int,db=Depends(get_db),user=Depends(current_user)):return controller.detail(db,id)
@router.post('/{id}/recalculate',response_model=RunOut)
def recalc(id:int,db=Depends(get_db),user=Depends(editor)):return controller.recalc(db,id)
@router.post('/{id}/retry',response_model=RunOut)
def retry(id:int,db=Depends(get_db),user=Depends(editor)):return controller.retry(db,id)
