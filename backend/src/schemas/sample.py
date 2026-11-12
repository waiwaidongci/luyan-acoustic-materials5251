from pydantic import BaseModel,Field,ConfigDict
class SampleInput(BaseModel):
    code:str=Field(min_length=2,max_length=40,pattern=r'^[A-Za-z0-9_-]+$')
    name:str=Field(min_length=2,max_length=100)
    family:str=Field(min_length=1,max_length=100)
    absorption:float=Field(ge=0,le=1,allow_inf_nan=False,strict=True)
    impact:float=Field(ge=0,le=1000,allow_inf_nan=False,strict=True)
    carbon:float=Field(ge=0,le=1000,allow_inf_nan=False,strict=True)
    price:float=Field(ge=0,le=10000,allow_inf_nan=False,strict=True)
    thickness:float=Field(ge=0,le=1000,allow_inf_nan=False,strict=True)
    batch:str=Field(default='',max_length=100)
class SampleOut(SampleInput):
    id:int
    model_config=ConfigDict(from_attributes=True)
