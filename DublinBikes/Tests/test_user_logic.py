import unittest
from DublinBikes.SqlCode.sql_utils import get_sql_engine
from DublinBikes.SqlCode.user_db import register_user, get_user_by_email, update_user_profile

class TestUserLogic(unittest.TestCase):
    """
    Test the user logic functions: registering a user, retrieving by email,
    and updating the user profile.
    """

    # Test user emails that will be used in these tests.
    TEST_USER_EMAILS = [
        "test_user_logic1@example.com",
        "test_user_logic2@example.com"
    ]



    def setUp(self) -> None:
        """
        No table-wide cleanup is performed here; instead, tests will register
        users using known test emails.
        """
        pass



    def tearDown(self) -> None:
        """
        Delete only the test users inserted by these tests.
        """
        conn = get_sql_engine()
        try:
            cursor = conn.cursor()
            for email in self.TEST_USER_EMAILS:
                cursor.execute("DELETE FROM user WHERE email = ?", (email,))
            conn.commit()
        finally:
            conn.close()



    def test_register_user_success(self) -> None:
        """
        Test that a new user is registered successfully and can be retrieved.
        """
        email = self.TEST_USER_EMAILS[0]
        result = register_user(email, "testuser", "Test", "User", "password123", 10)
        self.assertTrue(result, "User should be registered successfully.")
        user = get_user_by_email(email)
        self.assertIsNotNone(user, "Registered user should be retrievable.")
        self.assertEqual(user["username"], "testuser", "Username should match the registered value.")



    def test_register_user_duplicate(self) -> None:
        """
        Test that duplicate user registration fails (by email and username).
        """
        email = self.TEST_USER_EMAILS[0]
        # First registration should succeed.
        result1 = register_user(email, "dupuser", "Dup", "User", "password", 10)
        self.assertTrue(result1, "First registration should succeed.")

        # Duplicate email should fail.
        result2 = register_user(email, "dupuser2", "Dup", "User", "password", 10)
        self.assertFalse(result2, "Registration with duplicate email should fail.")

        # Duplicate username (with different email) should also fail.
        email2 = self.TEST_USER_EMAILS[1]
        result3 = register_user(email2, "dupuser", "Another", "User", "password", 10)
        self.assertFalse(result3, "Registration with duplicate username should fail.")



    def test_get_user_by_email_not_found(self) -> None:
        """
        Test that looking up a non-existent user returns None.
        """
        user = get_user_by_email("nonexistent@example.com")
        self.assertIsNone(user, "Should return None for a non-existent user.")



    def test_update_user_profile_success(self) -> None:
        """
        Test that a user’s profile is successfully updated.
        """
        email = self.TEST_USER_EMAILS[0]
        # Register a user first.
        register_user(email, "updateuser", "Update", "User", "oldpassword", 10)
        # Update the user's profile.
        update_result = update_user_profile(email, "updateduser", "Updated", "User", "newpassword", 20)
        self.assertTrue(update_result, "User profile update should succeed.")
        # Retrieve and verify the updated details.
        user = get_user_by_email(email)
        self.assertEqual(user["username"], "updateduser", "Username should be updated.")
        self.assertEqual(user["first_name"], "Updated", "First name should be updated.")
        self.assertEqual(user["password"], "newpassword", "Password should be updated.")
        self.assertEqual(user["default_station"], 20, "Default station should be updated.")



    def test_update_user_profile_duplicate(self) -> None:
        """
        Test that updating a user's profile to a username that already exists fails.
        """
        email1 = self.TEST_USER_EMAILS[0]
        email2 = self.TEST_USER_EMAILS[1]
        # Register two distinct users.
        register_user(email1, "user1", "User", "One", "pass1", 10)
        register_user(email2, "user2", "User", "Two", "pass2", 10)
        # Attempt to update user2's username to user1's username.
        update_result = update_user_profile(email2, "user1", "User", "Two", "pass2", 10)
        self.assertFalse(update_result, "Updating profile with duplicate username should fail.")

if __name__ == '__main__':
    unittest.main()
