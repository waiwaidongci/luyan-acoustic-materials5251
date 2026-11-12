import os
DATABASE_URL=os.getenv('DATABASE_URL','mysql+pymysql://material:material-demo-local@localhost:17727/material?charset=utf8mb4')
REDIS_URL=os.getenv('REDIS_URL','redis://localhost:6379/0')
ARTIFACTS_DIR=os.getenv('ARTIFACTS_DIR','/artifacts')
JWT_SECRET=os.getenv('JWT_SECRET','local-material-topsis-change-this-before-hosting')
SEED_DEMO=os.getenv('SEED_DEMO','false').lower()=='true'
