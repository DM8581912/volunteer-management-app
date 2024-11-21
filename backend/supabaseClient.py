import os
import bcrypt
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and/or Key not set in environment variables.")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def cleanup_user(username: str):
    """Delete a user from the database by username."""
    try:
        supabase.from_("usercredential").delete().eq("username", username).execute()
        print(f"User '{username}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting user '{username}':", e)

def create_user(username: str, password: str):
    """Create a new user with a hashed password."""
    hashed_password = hash_password(password)
    try:
        # Delete existing user to prevent duplicates
        cleanup_user(username)
        # Insert the new user
        supabase.from_("usercredential").insert({
            "username": username,
            "password": hashed_password
        }).execute()
        print(f"User '{username}' created successfully.")
    except Exception as e:
        print("Error creating user:", e)

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user by checking the password."""
    try:
        result = supabase.from_("usercredential").select("password").eq("username", username).execute()
        if result.data:
            stored_password = result.data[0]["password"]
            if verify_password(password, stored_password):
                print("Authentication successful.")
                return True
            else:
                print("Authentication failed: Incorrect password.")
        else:
            print("Authentication failed: User not found.")
        return False
    except Exception as e:
        print("Error during authentication:", e)
        return False

if __name__ == "__main__":
    # Example usage
    create_user("johndoe", "securepassword123")
    authenticate_user("johndoe", "securepassword123")
