from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import redis

from config import settings

SQL_ALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://"
    f"{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG)

SessionLocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, password=settings.REDIS_PASSWORD)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # pylint: disable=import-outside-toplevel
    # pylint: disable=unused-import
    from Entities import User, ServiceTypes, Tasks, UserPreferences, UserOTP
    Base.metadata.create_all(bind=engine)
