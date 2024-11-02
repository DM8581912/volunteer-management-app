import unittest
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from hashlib import sha256
from unittest.mock import patch, MagicMock

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class TestSupabaseClient(unittest.TestCase):
    def setUp(self):
        """Set up test data for each test."""
        self.test_username = "janedoe"
        self.test_password = sha256("password123".encode()).hexdigest()

        try:
            supabase.from_("usercredential").insert({
                "username": self.test_username,
                "password": self.test_password
            }).execute()
        except Exception as e:
            print("Error creating user:", e)

    def tearDown(self):
        """Remove test users after each test run"""
        try:
            supabase.from_("usercredential").delete().eq("username", self.test_username).execute()
        except Exception as e:
            print("Error during cleanup:", e)

    def test_fetch_user_profiles(self):
        """Test fetching user profiles from Supabase"""
        try:
            data = supabase.from_("userprofile").select("*").execute()
            print("User profiles fetched successfully:", data)
        except Exception as e:
            self.fail(f"Fetching user profiles failed with error: {e}")

    def test_fetch_user_credentials(self):
        """Test fetching user credentials from Supabase"""
        try:
            data = supabase.from_("usercredential").select("*").execute()
            print("User credentials fetched successfully:", data)
        except Exception as e:
            self.fail(f"Fetching user credentials failed with error: {e}")

    def test_authenticate_user(self):
        """Test user authentication with hashed password"""
        stored_password = supabase.from_("usercredential").select("password").eq("username", self.test_username).execute()
        if stored_password.data:
            self.assertEqual(stored_password.data[0]['password'], self.test_password)
        else:
            self.fail("User not found or password mismatch")

    def test_authenticate_nonexistent_user(self):
        """Test authentication for a nonexistent user"""
        non_existent_user = "nonexistent_user"
        stored_password = supabase.from_("usercredential").select("password").eq("username", non_existent_user).execute()
        self.assertEqual(len(stored_password.data), 0, "Nonexistent user should not be found")

    def test_fetch_user_profiles_with_error(self):
        """Test fetching user profiles with simulated error handling"""
        with patch.object(supabase, 'from_', side_effect=Exception("Database error")):
            try:
                supabase.from_("userprofile").select("*").execute()
            except Exception as e:
                self.assertIn("Database error", str(e))

    def test_fetch_user_credentials_with_error(self):
        """Test fetching user credentials with simulated error handling"""
        with patch.object(supabase, 'from_', side_effect=Exception("Database error")):
            try:
                supabase.from_("usercredential").select("*").execute()
            except Exception as e:
                self.assertIn("Database error", str(e))

if __name__ == "__main__":
    unittest.main()
