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
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)
class RunOut(RunSummary):
    snapshot:dict
    result:dict
