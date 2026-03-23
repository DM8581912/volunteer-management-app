"""Unit tests for supabaseClient.py - password hashing, user CRUD, and authentication."""

import pytest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Patch before import
with patch.dict(os.environ, {
    'SUPABASE_URL': 'https://fake.supabase.co',
    'SUPABASE_KEY': 'fake-key'
}):
    with patch('supabase.create_client', return_value=MagicMock()):
        for mod_name in list(sys.modules.keys()):
            if mod_name == 'supabaseClient':
                del sys.modules[mod_name]
        import supabaseClient as sc_module


class TestPasswordHashing:
    """Tests for hash_password and verify_password."""

    def test_hash_returns_string(self):
        result = sc_module.hash_password("testpassword")
        assert isinstance(result, str)

    def test_hash_is_not_plaintext(self):
        result = sc_module.hash_password("testpassword")
        assert result != "testpassword"

    def test_verify_correct_password(self):
        hashed = sc_module.hash_password("mypassword")
        assert sc_module.verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = sc_module.hash_password("mypassword")
        assert sc_module.verify_password("wrongpassword", hashed) is False

    def test_different_passwords_produce_different_hashes(self):
        hash1 = sc_module.hash_password("password1")
        hash2 = sc_module.hash_password("password2")
        assert hash1 != hash2

    def test_same_password_produces_different_hashes(self):
        hash1 = sc_module.hash_password("samepassword")
        hash2 = sc_module.hash_password("samepassword")
        assert hash1 != hash2  # different salts

    def test_empty_password(self):
        hashed = sc_module.hash_password("")
        assert sc_module.verify_password("", hashed) is True

    def test_unicode_password(self):
        hashed = sc_module.hash_password("p@ssw0rd!")
        assert sc_module.verify_password("p@ssw0rd!", hashed) is True


class TestCreateUser:
    """Tests for create_user function."""

    @patch.object(sc_module, 'supabase')
    def test_create_user_success(self, mock_supabase):
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock()
        mock_supabase.from_.return_value.insert.return_value.execute.return_value = MagicMock()
        result = sc_module.create_user("testuser", "password123")
        assert result is True

    @patch.object(sc_module, 'supabase')
    def test_create_user_failure(self, mock_supabase):
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock()
        mock_supabase.from_.return_value.insert.return_value.execute.side_effect = Exception("DB error")
        result = sc_module.create_user("testuser", "password123")
        assert result is False


class TestAuthenticateUser:
    """Tests for authenticate_user function."""

    @patch.object(sc_module, 'supabase')
    def test_authenticate_success(self, mock_supabase):
        hashed = sc_module.hash_password("correct123")
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"password": hashed}]
        )
        result = sc_module.authenticate_user("testuser", "correct123")
        assert result is True

    @patch.object(sc_module, 'supabase')
    def test_authenticate_wrong_password(self, mock_supabase):
        hashed = sc_module.hash_password("correct123")
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"password": hashed}]
        )
        result = sc_module.authenticate_user("testuser", "wrongpassword")
        assert result is False

    @patch.object(sc_module, 'supabase')
    def test_authenticate_user_not_found(self, mock_supabase):
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )
        result = sc_module.authenticate_user("ghost", "password")
        assert result is False

    @patch.object(sc_module, 'supabase')
    def test_authenticate_db_error(self, mock_supabase):
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("DB error")
        result = sc_module.authenticate_user("testuser", "password")
        assert result is False


class TestCleanupUser:
    """Tests for cleanup_user function."""

    @patch.object(sc_module, 'supabase')
    def test_cleanup_success(self, mock_supabase):
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock()
        result = sc_module.cleanup_user("testuser")
        assert result is True

    @patch.object(sc_module, 'supabase')
    def test_cleanup_failure(self, mock_supabase):
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception("Error")
        result = sc_module.cleanup_user("testuser")
        assert result is False
