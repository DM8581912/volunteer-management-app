"""Unit tests for the Flask application routes and helper functions.

Tests cover validation, match scoring, and API endpoint behavior
using Flask's test client with mocked Supabase calls.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Set env vars before any app imports
os.environ.setdefault('SUPABASE_URL', 'https://test.supabase.co')
os.environ.setdefault('SUPABASE_KEY', 'test-key-for-unit-tests')

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock supabase create_client before importing app
with patch('supabase.create_client', return_value=MagicMock()):
    from app import app, validate_data, calculate_match_score

import bcrypt


class TestValidateData(unittest.TestCase):
    """Tests for the validate_data helper function."""

    def test_valid_data_passes(self):
        schema = {'name': {'required': True, 'type': str, 'min_length': 2}}
        errors = validate_data({'name': 'Alice'}, schema)
        self.assertEqual(errors, [])

    def test_missing_required_field(self):
        schema = {'name': {'required': True, 'type': str}}
        errors = validate_data({}, schema)
        self.assertEqual(len(errors), 1)
        self.assertIn('name is required', errors[0])

    def test_wrong_type(self):
        schema = {'age': {'required': True, 'type': int}}
        errors = validate_data({'age': 'not a number'}, schema)
        self.assertTrue(any('type' in e for e in errors))

    def test_min_length_string(self):
        schema = {'name': {'required': True, 'type': str, 'min_length': 5}}
        errors = validate_data({'name': 'ab'}, schema)
        self.assertTrue(any('at least 5' in e for e in errors))

    def test_max_length_string(self):
        schema = {'name': {'required': True, 'type': str, 'max_length': 3}}
        errors = validate_data({'name': 'toolong'}, schema)
        self.assertTrue(any('must not exceed' in e for e in errors))

    def test_invalid_enum_value(self):
        schema = {'urgency': {'required': True, 'type': str, 'values': ['low', 'medium', 'high']}}
        errors = validate_data({'urgency': 'critical'}, schema)
        self.assertTrue(any('must be one of' in e for e in errors))

    def test_valid_enum_value(self):
        schema = {'urgency': {'required': True, 'type': str, 'values': ['low', 'medium', 'high']}}
        errors = validate_data({'urgency': 'high'}, schema)
        self.assertEqual(errors, [])

    def test_optional_field_absent(self):
        schema = {'bio': {'type': str, 'max_length': 100}}
        errors = validate_data({}, schema)
        self.assertEqual(errors, [])

    def test_empty_data_empty_schema(self):
        errors = validate_data({}, {})
        self.assertEqual(errors, [])

    def test_list_min_length(self):
        schema = {'skills': {'required': True, 'type': list, 'min_length': 1}}
        errors = validate_data({'skills': []}, schema)
        self.assertTrue(any('at least 1' in e for e in errors))

    def test_list_valid(self):
        schema = {'skills': {'required': True, 'type': list, 'min_length': 1}}
        errors = validate_data({'skills': ['python']}, schema)
        self.assertEqual(errors, [])


class TestCalculateMatchScore(unittest.TestCase):
    """Tests for the calculate_match_score function."""

    def test_perfect_match(self):
        score = calculate_match_score(['First Aid', 'CPR'], ['first aid', 'cpr'])
        self.assertEqual(score, 100.0)

    def test_partial_match(self):
        score = calculate_match_score(['First Aid'], ['First Aid', 'CPR'])
        self.assertEqual(score, 50.0)

    def test_no_match(self):
        score = calculate_match_score(['Cooking'], ['First Aid', 'CPR'])
        self.assertEqual(score, 0)

    def test_empty_volunteer_skills(self):
        score = calculate_match_score([], ['First Aid'])
        self.assertEqual(score, 0)

    def test_empty_event_skills(self):
        score = calculate_match_score(['First Aid'], [])
        self.assertEqual(score, 0)

    def test_both_empty(self):
        score = calculate_match_score([], [])
        self.assertEqual(score, 0)

    def test_none_volunteer_skills(self):
        score = calculate_match_score(None, ['First Aid'])
        self.assertEqual(score, 0)

    def test_none_event_skills(self):
        score = calculate_match_score(['First Aid'], None)
        self.assertEqual(score, 0)

    def test_case_insensitive(self):
        score = calculate_match_score(['FIRST AID'], ['first aid'])
        self.assertEqual(score, 100.0)

    def test_extra_volunteer_skills_ignored(self):
        score = calculate_match_score(
            ['First Aid', 'CPR', 'Cooking', 'Driving'],
            ['First Aid', 'CPR']
        )
        self.assertEqual(score, 100.0)


class TestRegisterEndpoint(unittest.TestCase):
    """Tests for the /register endpoint."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch('app.supabase')
    def test_register_success(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{}])

        response = self.client.post('/register', json={
            'username': 'newuser',
            'password': 'StrongPass1!',
            'email': 'new@example.com'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User registered successfully')

    @patch('app.supabase')
    def test_register_missing_fields(self, mock_supabase):
        response = self.client.post('/register', json={'username': 'user'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch('app.supabase')
    def test_register_short_password(self, mock_supabase):
        response = self.client.post('/register', json={
            'username': 'newuser',
            'password': 'short',
            'email': 'new@example.com'
        })
        self.assertEqual(response.status_code, 400)

    @patch('app.supabase')
    def test_register_duplicate_user(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{'username': 'existing'}]
        )

        response = self.client.post('/register', json={
            'username': 'existing',
            'password': 'StrongPass1!',
            'email': 'existing@example.com'
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'User already exists')


class TestLoginEndpoint(unittest.TestCase):
    """Tests for the /login endpoint."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch('app.supabase')
    def test_login_success(self, mock_supabase):
        hashed = bcrypt.hashpw(b'TestPass123', bcrypt.gensalt()).decode('utf-8')
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{'username': 'testuser', 'password': hashed}]
        )

        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Login successful')

    @patch('app.supabase')
    def test_login_wrong_password(self, mock_supabase):
        hashed = bcrypt.hashpw(b'CorrectPass', bcrypt.gensalt()).decode('utf-8')
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{'username': 'testuser', 'password': hashed}]
        )

        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'WrongPass'
        })
        self.assertEqual(response.status_code, 401)

    @patch('app.supabase')
    def test_login_nonexistent_user(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])

        response = self.client.post('/login', json={
            'username': 'ghost',
            'password': 'anything'
        })
        self.assertEqual(response.status_code, 401)

    def test_login_missing_credentials(self):
        response = self.client.post('/login', json={})
        self.assertEqual(response.status_code, 400)

    def test_login_empty_username(self):
        response = self.client.post('/login', json={
            'username': '',
            'password': 'something'
        })
        self.assertEqual(response.status_code, 400)


class TestEventFormEndpoint(unittest.TestCase):
    """Tests for the /eventform endpoint."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch('app.supabase')
    def test_get_events(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(
            data=[{'eventName': 'Test Event', 'location': 'NYC'}]
        )

        response = self.client.get('/eventform')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('events', data)
        self.assertEqual(len(data['events']), 1)

    @patch('app.supabase')
    def test_create_event_success(self, mock_supabase):
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{}])

        response = self.client.post('/eventform', json={
            'eventName': 'Charity Run',
            'location': 'Central Park',
            'requiredSkills': ['running', 'first aid'],
            'urgency': 'medium',
            'eventDate': '2026-12-01'
        })
        self.assertEqual(response.status_code, 201)

    @patch('app.supabase')
    def test_create_event_missing_fields(self, mock_supabase):
        response = self.client.post('/eventform', json={'eventName': 'Incomplete Event'})
        self.assertEqual(response.status_code, 400)

    @patch('app.supabase')
    def test_create_event_invalid_urgency(self, mock_supabase):
        response = self.client.post('/eventform', json={
            'eventName': 'Test Event',
            'location': 'NYC',
            'requiredSkills': ['aid'],
            'urgency': 'critical',
            'eventDate': '2026-12-01'
        })
        self.assertEqual(response.status_code, 400)

    @patch('app.supabase')
    def test_create_event_empty_skills(self, mock_supabase):
        response = self.client.post('/eventform', json={
            'eventName': 'Test Event',
            'location': 'NYC',
            'requiredSkills': [],
            'urgency': 'low',
            'eventDate': '2026-12-01'
        })
        self.assertEqual(response.status_code, 400)


class TestVolunteerMatchEndpoints(unittest.TestCase):
    """Tests for the /matches/* endpoints."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch('app.supabase')
    def test_get_event_matches_not_found(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])

        response = self.client.get('/matches/event/nonexistent')
        self.assertEqual(response.status_code, 404)

    @patch('app.supabase')
    def test_get_volunteer_matches_not_found(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])

        response = self.client.get('/matches/volunteer/ghost')
        self.assertEqual(response.status_code, 404)

    @patch('app.supabase')
    def test_get_volunteer_matches_success(self, mock_supabase):
        user_data = [{'username': 'alice', 'skills': ['First Aid', 'CPR']}]
        events_data = [
            {'eventName': 'Aid Event', 'requiredSkills': ['First Aid'], 'id': '1'},
            {'eventName': 'Cooking Event', 'requiredSkills': ['Cooking'], 'id': '2'},
        ]

        def table_side_effect(table_name):
            mock_table = MagicMock()
            if table_name == 'users':
                mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=user_data)
            elif table_name == 'events':
                mock_table.select.return_value.execute.return_value = MagicMock(data=events_data)
            return mock_table

        mock_supabase.table.side_effect = table_side_effect

        response = self.client.get('/matches/volunteer/alice')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('matches', data)
        self.assertEqual(len(data['matches']), 1)
        self.assertEqual(data['matches'][0]['event']['eventName'], 'Aid Event')


class TestNotificationEndpoints(unittest.TestCase):
    """Tests for the /notifications/* endpoints."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch('app.supabase')
    def test_get_notifications_empty(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])

        response = self.client.get('/notifications/testuser')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['notifications'], [])

    @patch('app.supabase')
    def test_get_notifications_with_data(self, mock_supabase):
        notif_data = [{'id': '1', 'message': 'Hello', 'read': False}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=notif_data
        )

        response = self.client.get('/notifications/testuser')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['notifications']), 1)

    @patch('app.supabase')
    def test_mark_notifications_read(self, mock_supabase):
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock()

        response = self.client.post('/notifications/testuser/mark-read', json={
            'notification_ids': ['id1', 'id2']
        })
        self.assertEqual(response.status_code, 200)

    def test_mark_notifications_no_ids(self):
        response = self.client.post('/notifications/testuser/mark-read', json={
            'notification_ids': []
        })
        self.assertEqual(response.status_code, 400)


class TestVolunteerHistoryEndpoints(unittest.TestCase):
    """Tests for the /volunteer/<username>/history endpoints."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    @patch('app.supabase')
    def test_get_history_success(self, mock_supabase):
        history_data = [{'eventname': 'Aid Event', 'location': 'NYC'}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=history_data
        )

        response = self.client.get('/volunteer/alice/history')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('history', data)
        self.assertEqual(data['username'], 'alice')

    @patch('app.supabase')
    def test_get_history_not_found(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])

        response = self.client.get('/volunteer/ghost/history')
        self.assertEqual(response.status_code, 404)

    @patch('app.supabase')
    def test_add_history_user_not_found(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])

        response = self.client.post('/volunteer/ghost/history', json={
            'eventName': 'Test',
            'location': 'NYC'
        })
        self.assertEqual(response.status_code, 404)

    @patch('app.supabase')
    def test_add_history_success(self, mock_supabase):
        def table_side_effect(table_name):
            mock_table = MagicMock()
            if table_name == 'users':
                mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{'username': 'alice'}]
                )
            elif table_name == 'volunteerhistory':
                mock_table.insert.return_value.execute.return_value = MagicMock(data=[{}])
            return mock_table

        mock_supabase.table.side_effect = table_side_effect

        response = self.client.post('/volunteer/alice/history', json={
            'eventName': 'Charity Run',
            'description': 'Annual charity run',
            'location': 'Central Park',
            'requiredSkills': ['running'],
            'urgency': 'medium',
            'eventDate': '2026-06-15',
            'participationStatus': 'completed'
        })
        self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
    unittest.main()
