from src.services import study_service as service
def index(db):return service.list_studies(db)
def create(db,data):return service.create_study(db,data)

def update(db,id,data):return service.update_study(db,id,data)
