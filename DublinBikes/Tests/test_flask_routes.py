"""
Tests for the Flask application routes.
"""

def test_home_route(flask_client):
    """
    Test that the home page returns a 200 status code.
    """
    response = flask_client.get("/")
    assert response.status_code == 200
    # Check for some content (e.g., the title or header)
    assert b"DUBLIN BIKES" in response.data

def test_login_route_get(flask_client):
    """
    Test the GET /login route.
    """
    response = flask_client.get("/login")
    assert response.status_code == 200
    assert b"Sign in" in response.data

def test_register_route_get(flask_client):
    """
    Test the GET /register route.
    """
    response = flask_client.get("/register")
    assert response.status_code == 200
    assert b"Create an Account" in response.data
