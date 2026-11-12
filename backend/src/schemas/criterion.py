from pydantic import BaseModel,Field,ConfigDict
from src.constants.enums import Direction,MetricCode
class CriterionInput(BaseModel):
    study_id:int
    code:MetricCode
    name:str=Field(min_length=1,max_length=100)
    unit:str=Field(max_length=50)
    direction:Direction
    center_weight:float=Field(gt=0,le=1000,allow_inf_nan=False,strict=True)
class CriterionOut(CriterionInput):
    id:int
    model_config=ConfigDict(from_attributes=True)
