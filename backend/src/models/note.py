from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class TrialNote(Base):
    __tablename__='trial_notes'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(140),unique=True)
    run_id:Mapped[int]=mapped_column(ForeignKey('decision_runs.id'))
    sample_id:Mapped[int]=mapped_column(ForeignKey('material_samples.id'))
    protocol:Mapped[str]=mapped_column(String(1800))
    status:Mapped[str]=mapped_column(String(20),default='draft')
    reviewer_note:Mapped[str]=mapped_column(String(1000),default='')
    reviewed_by:Mapped[str]=mapped_column(String(140),default='')
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
