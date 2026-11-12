from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class CandidateStudy(Base):
    __tablename__='candidate_studies'
    id:Mapped[int]=mapped_column(primary_key=True)
    code:Mapped[str]=mapped_column(String(40),unique=True)
    name:Mapped[str]=mapped_column(String(140))
    context:Mapped[str]=mapped_column(String(1000),default='')
    source_file:Mapped[str]=mapped_column(String(140),default='')
    material_ids:Mapped[list]=mapped_column(JSON,default=list)
