import time
from pathlib import Path
from sqlalchemy import select
from redis import Redis
from src.config.database import Session
from src.config.settings import REDIS_URL
from src.models import DecisionRun
from src.services.run_service import execute_run
redis=Redis.from_url(REDIS_URL)
while True:
    Path('/tmp/heartbeat').touch()
    with Session() as db:
        item=db.scalar(select(DecisionRun).where(DecisionRun.status.in_(['queued','running'])).order_by(DecisionRun.id))
        if item:execute_run(db,item.id)
        else:redis.brpop('material:runs',timeout=2)
    time.sleep(.1)
