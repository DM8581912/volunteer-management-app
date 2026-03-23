import logging
import os
import bcrypt
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and/or Key not set in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt and return a UTF-8 string."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt-hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def cleanup_user(username: str):
    """Delete a user from the database by username."""
    try:
        supabase.from_("usercredential").delete().eq("username", username).execute()
        logger.info("User '%s' deleted successfully.", username)
    except Exception as e:
        logger.error("Error deleting user '%s': %s", username, e)


def create_user(username: str, password: str):
    """Create a new user with a hashed password."""
    hashed_password = hash_password(password)
    try:
        cleanup_user(username)
        supabase.from_("usercredential").insert({
            "username": username,
            "password": hashed_password
        }).execute()
        logger.info("User '%s' created successfully.", username)
    except Exception as e:
        logger.error("Error creating user '%s': %s", username, e)


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user by checking the password against the stored hash."""
    try:
        result = supabase.from_("usercredential").select("password").eq("username", username).execute()
        if result.data:
            stored_password = result.data[0]["password"]
            if verify_password(password, stored_password):
                logger.info("Authentication successful for '%s'.", username)
                return True
            else:
                logger.warning("Authentication failed for '%s': incorrect password.", username)
        else:
            logger.warning("Authentication failed: user '%s' not found.", username)
        return False
    except Exception as e:
        logger.error("Error during authentication for '%s': %s", username, e)
        return False
