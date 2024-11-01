import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from the .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Check if URL and Key are set
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and/or Key not set in environment variables.")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test the connection by fetching data from the 'UserProfile' table
def fetch_user_profiles():
    try:
        data = supabase.from_("userprofile").select("*").execute()
        print("User profiles fetched successfully:", data)
    except Exception as e:
        print("Error fetching user profiles:", e)

# Call the function to test
if __name__ == "__main__":
    fetch_user_profiles()
