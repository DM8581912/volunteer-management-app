import logging
from typing import Optional

import bcrypt
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def cleanup_user(username: str) -> bool:
    """Delete a user from the database by username. Returns True on success."""
    try:
        supabase.from_("usercredential").delete().eq("username", username).execute()
        logger.info("User '%s' deleted successfully.", username)
        return True
    except Exception as e:
        logger.error("Error deleting user '%s': %s", username, e)
        return False


def create_user(username: str, password: str) -> bool:
    """Create a new user with a hashed password. Returns True on success."""
    hashed_password = hash_password(password)
    try:
        cleanup_user(username)
        supabase.from_("usercredential").insert({
            "username": username,
            "password": hashed_password
        }).execute()
        logger.info("User '%s' created successfully.", username)
        return True
    except Exception as e:
        logger.error("Error creating user '%s': %s", username, e)
        return False


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user by verifying password against stored hash."""
    try:
        result = supabase.from_("usercredential").select("password").eq("username", username).execute()
        if not result.data:
            logger.warning("Authentication failed: user '%s' not found.", username)
            return False

        stored_password = result.data[0]["password"]
        if verify_password(password, stored_password):
            logger.info("User '%s' authenticated successfully.", username)
            return True

        logger.warning("Authentication failed: incorrect password for '%s'.", username)
        return False
    except Exception as e:
        logger.error("Error during authentication for '%s': %s", username, e)
        return False
