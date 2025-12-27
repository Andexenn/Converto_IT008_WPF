"""conftest file"""
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from Database.connection import Base, get_db
from Core.security import hash_password

from Entities.user import User
from Entities.tasks import Tasks
from Entities.user_preferences import UserPreferences
from Entities.user_otp import UserOTP
from Entities.service_types import ServiceTypes
from Core.security import create_token

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    
    # seed data
    try:
        convert_service = ServiceTypes(ServiceTypeID = 1, ServiceName = "CONVERSION", ServiceDescription = "Convert from one fileformat to another fileformat")
        compress_service = ServiceTypes(ServiceTypeID = 2, ServiceName = "COMPRESSION", ServiceDescription = "Compress the file to smaller size")
        removebg_service = ServiceTypes(ServiceTypeID = 3, ServiceName = "BACKGROUND REMOVAL", ServiceDescription = "Remove background from image")

        db.add_all([convert_service, compress_service, removebg_service])
        db.commit()

    except Exception as e:
        raise e 
    finally:
        db.close()

    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

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
def test_user_factory(db_session):
    def _create_test_user(email: str = "test@gmail.com", password: str = "hungdepzai123"):
        user = User(
            FirstName="Ryan",
            LastName="Andexen",
            Email=email,
            City="HCMC",
            HashedPassword=hash_password(password)
        )

        try:
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
        except Exception as e:
            db_session.rollback()
            raise e 
        finally:
            db_session.close()
        return user
    return _create_test_user

@pytest.fixture(scope="function")
def created_user(test_user_factory, db_session):

    user = db_session.query(User).filter(User.Email == "test@gmail.com").first()

    if user:
        return user 

    return test_user_factory(email="test@gmail.com")

@pytest.fixture(scope="function")
def access_token(created_user):
    access_token_expires = timedelta(minutes=90)

    email = created_user.Email
    user_id = created_user.UserID

    data = {
        "sub": email,
        "user_id": user_id,
        "email": email
    }

    return create_token(data=data, expires_delta=access_token_expires)

@pytest.fixture(scope="function")
def authorized_client(client, access_token):

    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {access_token}"
    }

    return client
