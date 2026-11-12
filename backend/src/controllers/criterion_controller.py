from src.services import criterion_service as service
def index(db,study_id):return service.list_criteria(db,study_id)
def create(db,data):return service.create_criterion(db,data)

def update(db,id,data):return service.update_criterion(db,id,data)
