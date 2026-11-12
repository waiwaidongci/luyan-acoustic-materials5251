from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class Criterion(Base):
    __tablename__='criteria'
    id:Mapped[int]=mapped_column(primary_key=True)
    study_id:Mapped[int]=mapped_column(ForeignKey('candidate_studies.id'))
    code:Mapped[str]=mapped_column(String(30))
    name:Mapped[str]=mapped_column(String(100))
    unit:Mapped[str]=mapped_column(String(50))
    direction:Mapped[str]=mapped_column(String(20))
    center_weight:Mapped[float]=mapped_column(DOUBLE(asdecimal=False))
    __table_args__=(UniqueConstraint('study_id','code'),)
