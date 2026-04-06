"""Run: python seed_db.py"""
import sys
sys.path.insert(0, ".")
from app.database import SessionLocal, engine, Base
from app.models import *  # noqa: ensure all models registered
from app.seed.seed_data import seed_database

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    result = seed_database(db)
    print(result)
finally:
    db.close()
