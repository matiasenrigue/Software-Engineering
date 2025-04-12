import unittest
import json
from DublinBikes.FlaskApp import app
from DublinBikes.SqlCode.sql_utils import get_sql_engine

class TestFlaskRoutes(unittest.TestCase):
    """
    Test the Flask routes including the home page, station view,
    API endpoints, and the user authentication flows.
    """
    
    

    # List of test emails that will be inserted during tests.
    TEST_USER_EMAILS = [
        "webtest@example.com",
        "login@example.com",
        "edit@example.com"
    ]

    
    
    
    def setUp(self) -> None:
        """
        Set up the Flask test client.
        """
        app.testing = True
        self.client = app.test_client()

    
    
    
    def tearDown(self) -> None:
        """
        Delete only the rows inserted by tests based on the known test emails.
        This avoids deleting production data from the user table.
        """
        conn = get_sql_engine()
        try:
            cursor = conn.cursor()
            for email in self.TEST_USER_EMAILS:
                cursor.execute("DELETE FROM user WHERE email = ?", (email,))
            conn.commit()
        finally:
            conn.close()

    
    
    
    def test_home_route(self) -> None:
        """
        Test that the home page loads and contains expected content.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"DUBLIN BIKES", response.data, "Home page should contain 'DUBLIN BIKES'.")

    
    
    
    def test_station_route_not_found(self) -> None:
        """
        Test that accessing a non-existent station returns a 404 status code.
        """
        response = self.client.get("/station/99999")
        self.assertEqual(response.status_code, 404)

    
    
    
    def test_api_current_weather(self) -> None:
        """
        Test that the current weather API returns JSON with the 'temp' key.
        """
        response = self.client.get("/api/current_weather")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        self.assertIn("temp", data, "Current weather data should contain 'temp' key.")

    
    
    
    def test_api_forecast_weather_missing_target(self) -> None:
        """
        Test that the forecast weather API returns a 400 error if 'target_datetime' is missing.
        """
        response = self.client.get("/api/forecast_weather?forecast_type=hourly")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data, "Response should contain an error message when target_datetime is missing.")

    
    
    
    def test_api_current_bikes(self) -> None:
        """
        Test that the current bikes API returns a JSON list.
        """
        response = self.client.get("/api/current_bikes")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list, "Current bikes data should be returned as a list.")

    
    
    
    def test_register_route_get(self) -> None:
        """
        Test that the registration page (GET /register) loads correctly.
        """
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create an Account", response.data)

    
    
    
    def test_register_route_post_success(self) -> None:
        """
        Test that a POST to /register with valid data successfully registers a user.
        """
        form_data = {
            "email": "webtest@example.com",
            "username": "webtest",
            "first_name": "Web",
            "last_name": "Tester",
            "password": "testpass",
            "default_station": "10"
        }
        response = self.client.post("/register", data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # After successful registration, the login page should be shown.
        self.assertIn(b"Sign in", response.data, "After registration, the user should be redirected to the login page.")

    
    
    
    def test_login_logout_flow(self) -> None:
        """
        Test the full login and logout flow by simulating registration via the /register route.
        """
        # Register a user through the route (this hashes the password properly).
        registration_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "first_name": "Login",
            "last_name": "User",
            "password": "loginpass",
            "default_station": "10"
        }
        reg_response = self.client.post("/register", data=registration_data, follow_redirects=True)
        self.assertEqual(reg_response.status_code, 200)
        self.assertIn(b"Sign in", reg_response.data, "After registration, should redirect to login.")

        # Log in with the newly registered user.
        login_data = {
            "email": "login@example.com",
            "password": "loginpass"
        }
        login_response = self.client.post("/login", data=login_data, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b"Welcome, loginuser", login_response.data, "After login, the home page should welcome the user.")

        # Log out the user.
        logout_response = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(logout_response.status_code, 200)
        self.assertNotIn(b"Welcome, loginuser", logout_response.data, "After logout, the user should no longer be welcomed.")

    
    
    
    def test_edit_profile_requires_login(self) -> None:
        """
        Test that accessing the edit profile page without logging in redirects to the login page.
        """
        response = self.client.get("/edit_profile", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sign in", response.data, "Accessing edit profile without login should redirect to the login page.")

    
    
    
    def test_edit_profile_post(self) -> None:
        """
        Test that a logged-in user can successfully update their profile.
        """
        # Register a user via the /register route.
        registration_data = {
            "email": "edit@example.com",
            "username": "edituser",
            "first_name": "Edit",
            "last_name": "User",
            "password": "editpass",
            "default_station": "10"
        }
        reg_response = self.client.post("/register", data=registration_data, follow_redirects=True)
        self.assertEqual(reg_response.status_code, 200)
        self.assertIn(b"Sign in", reg_response.data, "After registration, should redirect to login.")

        # Log in with the new user.
        login_data = {
            "email": "edit@example.com",
            "password": "editpass"
        }
        self.client.post("/login", data=login_data, follow_redirects=True)
        # Now update the profile.
        new_profile_data = {
            "username": "editeduser",
            "first_name": "Edited",
            "last_name": "User",
            "password": "neweditpass",
            "default_station": "10"
        }
        update_response = self.client.post("/edit_profile", data=new_profile_data, follow_redirects=True)
        self.assertEqual(update_response.status_code, 200)
        # self.assertIn(b"Profile updated successfully", update_response.data, "Profile update should be successful.")

if __name__ == '__main__':
    unittest.main()
