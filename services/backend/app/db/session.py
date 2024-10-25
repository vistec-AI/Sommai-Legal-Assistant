from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Prepare URL for an engine
url = URL.create(
    "postgresql+psycopg2",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)
engine = create_engine(url, pool_pre_ping=True)
# SessionLocal = Session(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
