"""Test connection file"""

### test server health ###
def test_connect_server(client, base_url):
    response = client.get(f"{base_url}/health")

    assert response.status_code == 200, "Server is unhealthy"
    assert response.json() == {"status": "healthy"}

### test connection to database ###
def test_connect_db(client, base_url):
    response = client.get(f"{base_url}/connect_db")

    assert response.status_code == 200, "Server failed to connecto to db"
    assert response.json() == {"status": "connected"}