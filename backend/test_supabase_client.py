# test_supabase_client.py

import unittest
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class TestSupabaseClient(unittest.TestCase):
    def test_fetch_user_profiles(self):
        """Test fetching user profiles from Supabase"""
        try:
            # Use lowercase table name
            data = supabase.from_("userprofile").select("*").execute()
            print("User profiles fetched successfully:", data)
        except Exception as e:
            self.fail(f"Fetching user profiles failed with error: {e}")

    def test_fetch_user_credentials(self):
        """Test fetching user credentials from Supabase"""
        try:
            # Use lowercase table name
            data = supabase.from_("usercredential").select("*").execute()
            print("User credentials fetched successfully:", data)
        except Exception as e:
            self.fail(f"Fetching user credentials failed with error: {e}")

if __name__ == "__main__":
    unittest.main()
