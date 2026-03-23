"""Unit tests for app.py - validation, matching logic, and route handlers."""

import json
import pytest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Patch supabase client creation before importing app
with patch.dict(os.environ, {
    'SUPABASE_URL': 'https://fake.supabase.co',
    'SUPABASE_KEY': 'fake-key'
}):
    with patch('supabase.create_client', return_value=MagicMock()):
        # Clear any cached modules
        for mod_name in list(sys.modules.keys()):
            if mod_name in ('app', 'reporting'):
                del sys.modules[mod_name]
        import app as app_module


# --- Tests for validate_data ---

class TestValidateData:
    """Tests for the validate_data function."""

    def test_valid_user_data(self):
        data = {
            'username': 'testuser',
            'password': 'secure123',
            'email': 'test@example.com',
            'skills': ['python'],
            'preferences': 'remote'
        }
        errors = app_module.validate_data(data, app_module.USER_SCHEMA)
        assert errors == []

    def test_missing_required_field(self):
        data = {'password': 'secure123', 'email': 'test@example.com'}
        errors = app_module.validate_data(data, app_module.USER_SCHEMA)
        assert any('username is required' in e for e in errors)

    def test_all_required_fields_missing(self):
        data = {}
        errors = app_module.validate_data(data, app_module.USER_SCHEMA)
        assert len(errors) == 3  # username, password, email

    def test_wrong_type(self):
        data = {
            'username': 'testuser',
            'password': 'secure123',
            'email': 'test@example.com',
            'skills': 'should_be_list'
        }
        errors = app_module.validate_data(data, app_module.USER_SCHEMA)
        assert any('skills' in e and 'type' in e for e in errors)

    def test_min_length_violation(self):
        data = {
            'username': 'ab',  # min 3
            'password': 'secure123',
            'email': 'test@example.com'
        }
        errors = app_module.validate_data(data, app_module.USER_SCHEMA)
        assert any('username' in e and 'at least 3' in e for e in errors)

    def test_max_length_violation(self):
        data = {
            'username': 'testuser',
            'password': 'secure123',
            'email': 'x' * 51  # max 50
        }
        errors = app_module.validate_data(data, app_module.USER_SCHEMA)
        assert any('email' in e and 'exceed' in e for e in errors)

    def test_invalid_enum_value(self):
        data = {
            'eventName': 'Test Event Name',
            'location': 'NYC',
            'requiredSkills': ['python'],
            'urgency': 'critical',  # not in ['low', 'medium', 'high']
            'eventDate': '2025-01-01'
        }
        errors = app_module.validate_data(data, app_module.EVENT_SCHEMA)
        assert any('urgency' in e and 'one of' in e for e in errors)

    def test_valid_event_data(self):
        data = {
            'eventName': 'Community Cleanup',
            'location': 'Central Park',
            'requiredSkills': ['organizing'],
            'urgency': 'high',
            'eventDate': '2025-06-15'
        }
        errors = app_module.validate_data(data, app_module.EVENT_SCHEMA)
        assert errors == []

    def test_optional_fields_skipped(self):
        data = {
            'username': 'testuser',
            'password': 'secure123',
            'email': 'test@example.com'
        }
        errors = app_module.validate_data(data, app_module.USER_SCHEMA)
        assert errors == []

    def test_empty_string_passes_type_check(self):
        data = {
            'eventName': '',  # passes type check but fails min_length
            'location': 'NYC',
            'requiredSkills': ['python'],
            'urgency': 'low',
            'eventDate': '2025-01-01'
        }
        errors = app_module.validate_data(data, app_module.EVENT_SCHEMA)
        assert any('eventName' in e and 'at least' in e for e in errors)


# --- Tests for calculate_match_score ---

class TestCalculateMatchScore:
    """Tests for the calculate_match_score function."""

    def test_perfect_match(self):
        score = app_module.calculate_match_score(['python', 'flask'], ['python', 'flask'])
        assert score == 100.0

    def test_partial_match(self):
        score = app_module.calculate_match_score(['python'], ['python', 'flask'])
        assert score == 50.0

    def test_no_match(self):
        score = app_module.calculate_match_score(['java'], ['python', 'flask'])
        assert score == 0.0

    def test_case_insensitive(self):
        score = app_module.calculate_match_score(['Python', 'FLASK'], ['python', 'flask'])
        assert score == 100.0

    def test_empty_volunteer_skills(self):
        score = app_module.calculate_match_score([], ['python'])
        assert score == 0.0

    def test_empty_event_skills(self):
        score = app_module.calculate_match_score(['python'], [])
        assert score == 0.0

    def test_both_empty(self):
        score = app_module.calculate_match_score([], [])
        assert score == 0.0

    def test_none_volunteer_skills(self):
        score = app_module.calculate_match_score(None, ['python'])
        assert score == 0.0

    def test_none_event_skills(self):
        score = app_module.calculate_match_score(['python'], None)
        assert score == 0.0

    def test_superset_volunteer_skills(self):
        score = app_module.calculate_match_score(
            ['python', 'flask', 'sql', 'docker'],
            ['python', 'flask']
        )
        assert score == 100.0


# --- Tests for find_best_matches ---

class TestFindBestMatches:
    """Tests for the find_best_matches function."""

    @patch.object(app_module, 'get_all_users')
    def test_returns_matches_above_threshold(self, mock_get_users):
        mock_get_users.return_value = [
            {'username': 'alice', 'skills': ['python', 'flask'], 'email': 'alice@test.com'},
            {'username': 'bob', 'skills': ['java'], 'email': 'bob@test.com'},
        ]
        event = {'eventName': 'PyCon', 'requiredSkills': ['python', 'flask']}
        matches = app_module.find_best_matches(event)
        assert len(matches) == 1
        assert matches[0]['username'] == 'alice'
        assert matches[0]['score'] == 100.0

    @patch.object(app_module, 'get_all_users')
    def test_no_matches_below_threshold(self, mock_get_users):
        mock_get_users.return_value = [
            {'username': 'bob', 'skills': ['java'], 'email': 'bob@test.com'},
        ]
        event = {'eventName': 'PyCon', 'requiredSkills': ['python', 'flask']}
        matches = app_module.find_best_matches(event)
        assert len(matches) == 0

    @patch.object(app_module, 'get_all_users')
    def test_respects_max_matches(self, mock_get_users):
        mock_get_users.return_value = [
            {'username': f'user{i}', 'skills': ['python', 'flask'], 'email': f'u{i}@test.com'}
            for i in range(10)
        ]
        event = {'eventName': 'PyCon', 'requiredSkills': ['python', 'flask']}
        matches = app_module.find_best_matches(event, max_matches=3)
        assert len(matches) == 3

    @patch.object(app_module, 'get_all_users')
    def test_skips_users_without_skills(self, mock_get_users):
        mock_get_users.return_value = [
            {'username': 'alice', 'email': 'alice@test.com'},  # no skills key
            {'username': 'bob', 'skills': None, 'email': 'bob@test.com'},
        ]
        event = {'eventName': 'PyCon', 'requiredSkills': ['python']}
        matches = app_module.find_best_matches(event)
        assert len(matches) == 0

    @patch.object(app_module, 'get_all_users')
    def test_sorted_by_score_descending(self, mock_get_users):
        mock_get_users.return_value = [
            {'username': 'partial', 'skills': ['python'], 'email': 'p@test.com'},
            {'username': 'full', 'skills': ['python', 'flask', 'sql'], 'email': 'f@test.com'},
        ]
        event = {'eventName': 'PyCon', 'requiredSkills': ['python', 'flask', 'sql']}
        matches = app_module.find_best_matches(event)
        assert matches[0]['username'] == 'full'

    @patch.object(app_module, 'get_all_users')
    def test_empty_user_list(self, mock_get_users):
        mock_get_users.return_value = []
        event = {'eventName': 'PyCon', 'requiredSkills': ['python']}
        matches = app_module.find_best_matches(event)
        assert matches == []


# --- Tests for Flask Route Handlers ---

class TestRoutes:
    """Tests for Flask API routes."""

    @pytest.fixture(autouse=True)
    def setup(self):
        app_module.app.config['TESTING'] = True
        self.client = app_module.app.test_client()

    @patch.object(app_module, 'supabase')
    @patch.object(app_module, 'get_user', return_value=None)
    def test_register_success(self, mock_get_user, mock_supabase):
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()
        response = self.client.post('/register', json={
            'username': 'newuser',
            'password': 'secure123',
            'email': 'new@test.com'
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User registered successfully'
        assert 'password' not in data.get('user', {})

    def test_register_missing_fields(self):
        response = self.client.post('/register', json={
            'username': 'newuser'
        })
        assert response.status_code == 400

    @patch.object(app_module, 'get_user', return_value={'username': 'existing'})
    def test_register_duplicate_user(self, mock_get_user):
        response = self.client.post('/register', json={
            'username': 'existing',
            'password': 'secure123',
            'email': 'test@test.com'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error']

    def test_login_success(self):
        import bcrypt
        hashed = bcrypt.hashpw('correct123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        with patch.object(app_module, 'get_user', return_value={
            'username': 'testuser',
            'password': hashed
        }):
            response = self.client.post('/login', json={
                'username': 'testuser',
                'password': 'correct123'
            })
            assert response.status_code == 200

    def test_login_invalid_credentials(self):
        import bcrypt
        hashed = bcrypt.hashpw('correct123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        with patch.object(app_module, 'get_user', return_value={
            'username': 'testuser',
            'password': hashed
        }):
            response = self.client.post('/login', json={
                'username': 'testuser',
                'password': 'wrongpassword'
            })
            assert response.status_code == 401

    def test_login_missing_fields(self):
        response = self.client.post('/login', json={})
        assert response.status_code == 400

    @patch.object(app_module, 'get_user', return_value=None)
    def test_login_user_not_found(self, mock_get_user):
        response = self.client.post('/login', json={
            'username': 'ghost',
            'password': 'pass123'
        })
        assert response.status_code == 401

    @patch.object(app_module, 'get_all_events')
    def test_get_events(self, mock_get_events):
        mock_get_events.return_value = [{'eventName': 'Cleanup', 'location': 'Park'}]
        response = self.client.get('/eventform')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['events']) == 1

    @patch.object(app_module, 'get_all_events')
    def test_get_events_empty(self, mock_get_events):
        mock_get_events.return_value = []
        response = self.client.get('/eventform')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['events'] == []

    @patch.object(app_module, 'supabase')
    def test_create_event_success(self, mock_supabase):
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()
        response = self.client.post('/eventform', json={
            'eventName': 'Community Cleanup',
            'location': 'Central Park',
            'requiredSkills': ['organizing'],
            'urgency': 'high',
            'eventDate': '2025-06-15'
        })
        assert response.status_code == 201

    def test_create_event_invalid_data(self):
        response = self.client.post('/eventform', json={
            'eventName': 'Hi',  # too short
            'location': 'NYC'
        })
        assert response.status_code == 400

    @patch.object(app_module, 'get_user', return_value=None)
    def test_get_volunteer_matches_user_not_found(self, mock_get_user):
        response = self.client.get('/matches/volunteer/ghost')
        assert response.status_code == 404

    @patch.object(app_module, 'get_user_notifications')
    def test_get_notifications(self, mock_get_notifs):
        mock_get_notifs.return_value = [{'id': '1', 'message': 'Test', 'read': False}]
        response = self.client.get('/notifications/testuser')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['notifications']) == 1

    @patch.object(app_module, 'get_user_notifications')
    def test_get_notifications_empty(self, mock_get_notifs):
        mock_get_notifs.return_value = []
        response = self.client.get('/notifications/testuser')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['notifications'] == []

    def test_mark_notifications_read_no_ids(self):
        response = self.client.post('/notifications/testuser/mark-read',
                                     json={'notification_ids': []})
        assert response.status_code == 400

    @patch.object(app_module, 'supabase')
    def test_volunteer_history_not_found(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        response = self.client.get('/volunteer/ghost/history')
        assert response.status_code == 404

    @patch.object(app_module, 'get_user', return_value=None)
    def test_add_volunteer_event_user_not_found(self, mock_get_user):
        response = self.client.post('/volunteer/ghost/history', json={
            'eventName': 'Test',
            'location': 'NYC'
        })
        assert response.status_code == 404
