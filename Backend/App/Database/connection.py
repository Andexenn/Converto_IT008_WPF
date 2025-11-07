from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings 

SQL_ALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG)

SessionLocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

def init_db():
    from Entities import User, Wallet, WalletTransaction, Service, ConversionHistory
    Base.metadata.create_all(bind=engine)





