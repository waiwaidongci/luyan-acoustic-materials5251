from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class DecisionRun(Base):
    __tablename__='decision_runs'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(140),unique=True)
    study_id:Mapped[int]=mapped_column(ForeignKey('candidate_studies.id'))
    center_weights:Mapped[dict]=mapped_column(JSON)
    concentration:Mapped[float]=mapped_column(DOUBLE(asdecimal=False),default=40.)
    repeats:Mapped[int]=mapped_column(default=1000)
    seed:Mapped[int]=mapped_column(default=20261112)
    status:Mapped[str]=mapped_column(String(20),default='queued')
    snapshot:Mapped[dict]=mapped_column(JSON,default=dict)
    summary:Mapped[dict]=mapped_column(JSON,default=dict)
    result:Mapped[dict]=mapped_column(JSON,default=dict)
    error:Mapped[str]=mapped_column(String(600),default='')
    # Source-data provenance and recalculation lineage (migration 002).
    source_fingerprint:Mapped[str]=mapped_column(String(64),default='')
    source_signature:Mapped[dict]=mapped_column(JSON,default=dict)
    recalc_of_id:Mapped[int|None]=mapped_column(ForeignKey('decision_runs.id'),nullable=True,default=None)
    recalc_seq:Mapped[int]=mapped_column(default=0)
    recalc_status:Mapped[str]=mapped_column(String(20),default='')
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
