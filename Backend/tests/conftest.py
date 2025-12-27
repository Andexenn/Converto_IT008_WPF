"""conftest file"""
import pytest 
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from Database.connection import Base, get_db
from Core.security import hash_password

# Import ALL entities to ensure they're registered
from Entities.user import User
from Entities.tasks import Tasks
from Entities.user_preferences import UserPreferences
from Entities.user_otp import UserOTP
from Entities.service_types import ServiceTypes

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c 

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:5050"

@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def create_test_user(db_session):
    def _create_test_user(email: str = "test@gmail.com", password: str = "hungdepzai123"):
        user = User(
            FirstName="Ryan",
            LastName="Andexen",
            Email=email,
            City="HCMC",
            HashedPassword=hash_password(password)
        )

        db_session.add(user)
        db_session.commit()
        
        return user 
    return _create_test_user