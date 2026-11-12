from pydantic import BaseModel,Field,ConfigDict
class StudyInput(BaseModel):
    code:str=Field(min_length=2,max_length=40,pattern=r'^[A-Za-z0-9_-]+$')
    name:str=Field(min_length=2,max_length=140)
    context:str=Field(default='',max_length=1000)
    source_file:str=Field(default='',max_length=140)
    material_ids:list[int]=Field(default_factory=list,max_length=120)
class StudyOut(StudyInput):
    id:int
    model_config=ConfigDict(from_attributes=True)
