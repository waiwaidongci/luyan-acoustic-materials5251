from pydantic import BaseModel,Field,ConfigDict
from datetime import datetime
from typing import Annotated
Positive=Annotated[float,Field(gt=0,le=1000,allow_inf_nan=False,strict=True)]
class RunInput(BaseModel):
    name:str=Field(min_length=2,max_length=140)
    study_id:int
    center_weights:dict[str,Positive]=Field(default_factory=dict)
    concentration:float=Field(default=40,ge=.1,le=10000,allow_inf_nan=False,strict=True)
    repeats:int=Field(default=1000,ge=1000,le=2000,strict=True)
    seed:int=Field(default=20261112,ge=0,le=2147483647,strict=True)
class RunSummary(RunInput):
    id:int
    status:str
    summary:dict
    error:str
    source_fingerprint:str=''
    recalc_of_id:int|None=None
    recalc_seq:int=0
    recalc_status:str=''
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)
class RunOut(RunSummary):
    snapshot:dict
    result:dict
class SourceChange(BaseModel):
    model_config=ConfigDict(extra='allow')
class StaleReport(BaseModel):
    run_id:int
    name:str
    study_id:int
    status:str
    stale:bool
    source_fingerprint:str
    current_fingerprint:str
    sample_changes:list[dict]
    criterion_changes:list[dict]
    affected_sample_ids:list[int]
    recalc_of_id:int|None=None
    recalc_seq:int=0
    recalc_status:str=''
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)
class RecalcResult(BaseModel):
    queued:list[dict]
    skipped:list[dict]
    up_to_date:list[dict]
class BatchRecalcInput(BaseModel):
    study_id:int|None=None
