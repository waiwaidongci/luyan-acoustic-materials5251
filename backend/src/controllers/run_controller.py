from src.services import run_service as service
def index(db):return service.list_runs(db)
def create(db,data):return service.create_run(db,data)

def detail(db,id):return service.get_run(db,id)
def stale(db,study_id=None):return service.list_stale(db,study_id)
def recalc(db,id):return service.recalculate_run(db,id)
def retry(db,id):return service.retry_recalc(db,id)
def batch_recalc(db,data):return service.recalculate_stale(db,data.study_id)
