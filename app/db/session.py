##database connection with sqlalchemy 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import os

# Engine — Database-உடன் connection
engine = create_engine(settings.DATABASE_URL)

# Session — Database operations பண்ண
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base — எல்லா models-உம் இதை inherit பண்ணும்
Base = declarative_base()

# Dependency — FastAPI-ல use பண்ண
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()