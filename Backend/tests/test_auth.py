"""Test auth file"""
from Entities.user import User
from Schemas.user import UserLogin, UserCreate

### Test signup ###

def test_signup(client, base_url, db_session):
    data = {
        "FirstName": "Ryan",
        "LastName": "Andexen",
        "Email": "hung123@gmail.com",
        "Password": "Unhu0412*"
    }
    
    try:
        response = client.post(f"{base_url}/api/auth/signup", json = data)
        assert response.status_code == 201, response.text
    except Exception as e:
        assert 1 == 2, f"Failed to sin up: {str(e)}"
    # response_data = response.json()
    # assert response_data["FirstName"] == "Ryan"
    # assert response_data["Email"] == "hung123@gmail.com"

    db = db_session
    db.expire_all()

    user_signup = db.query(User).filter(User.Email == data.get("Email")).first()

    assert user_signup is not None, "Failed to save to database"
    assert user_signup.FirstName == "Ryan", "FirstName is not correct"


### Test login ###

def test_login(client, base_url, create_test_user):
    email = "hungdepzai@gmail.com"
    password = "hungdepzai123"

    create_test_user(email=email, password=password)

    payload = {
        "Email": email,
        "Password": password
    }

    try:
        response = client.post(f"{base_url}/api/auth/login", json = payload)

        assert response.status_code == 200, response.text

        data = response.json()

        assert "access_token" in data, "Lacking access token in login response"
        assert "refresh_token" in data, "Lacking refresh token in login response"

    except Exception as e:
        assert 1 == 2, f"Failed to login due to: {str(e)}" 

    
