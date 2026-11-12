from src.services import sample_service as service
def index(db):return service.list_samples(db)
def create(db,data):return service.create_sample(db,data)

def update(db,id,data):return service.update_sample(db,id,data)
