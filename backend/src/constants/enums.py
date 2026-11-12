from enum import StrEnum
class Role(StrEnum):
    ADMIN='admin'; ANALYST='analyst'; VIEWER='viewer'
class RunStatus(StrEnum):
    QUEUED='queued'; RUNNING='running'; COMPLETED='completed'; FAILED='failed'
class NoteStatus(StrEnum):
    DRAFT='draft'; APPROVED='approved'; REJECTED='rejected'
class Direction(StrEnum):
    BENEFIT='benefit'; COST='cost'
class MetricCode(StrEnum):
    ABSORPTION='absorption'; IMPACT='impact'; CARBON='carbon'; PRICE='price'; THICKNESS='thickness'
