from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class MaterialSample(Base):
    __tablename__='material_samples'
    id:Mapped[int]=mapped_column(primary_key=True)
    code:Mapped[str]=mapped_column(String(40),unique=True)
    name:Mapped[str]=mapped_column(String(100))
    family:Mapped[str]=mapped_column(String(100))
    absorption:Mapped[float]=mapped_column(DOUBLE(asdecimal=False))
    impact:Mapped[float]=mapped_column(DOUBLE(asdecimal=False))
    carbon:Mapped[float]=mapped_column(DOUBLE(asdecimal=False))
    price:Mapped[float]=mapped_column(DOUBLE(asdecimal=False))
    thickness:Mapped[float]=mapped_column(DOUBLE(asdecimal=False))
    batch:Mapped[str]=mapped_column(String(100),default='')
