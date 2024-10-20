import unittest
from flask import json
from app import app, db

class VolunteerHistoryTestCase(unittest.TestCase):
    def setUp(self):
        """Sets up a test client and initializes test data"""
        self.app = app.test_client()
        self.app.testing = True

        # Create a sample user with history
        self.sample_user = {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'skills': ['Registration', 'First Aid'],
            'preferences': 'Weekend events preferred',
            'history': [
                {
                    'eventName': 'Houston Marathon',
                    'description': 'Gave water to runners',
                    'location': 'Houston, TX',
                    'requiredSkills': ['Water Station Management'],
                    'urgency': 'high',
                    'eventDate': '2023-01-15T09:00:00.000Z',
                    'participationStatus': 'completed'
                }
            ]
        }
        
        # Clear the database and add the test user
        db['users'] = [self.sample_user]

    def tearDown(self):
        """Cleans up the test database after each test"""
        db['users'].clear()

    def test_get_volunteer_history(self):
        """Test fetching volunteer history for an existing user"""
        response = self.app.get(f'/volunteer/{self.sample_user["username"]}/history')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify response structure
        self.assertIn('username', data)
        self.assertIn('history', data)
        self.assertEqual(data['username'], self.sample_user['username'])
        self.assertEqual(len(data['history']), 1)
        
        # Verify event details
        event = data['history'][0]
        self.assertEqual(event['eventName'], 'Houston Marathon')
        self.assertEqual(event['location'], 'Houston, TX')
        self.assertIsInstance(event['requiredSkills'], list)

    def test_get_volunteer_history_nonexistent_user(self):
        """Test fetching history for a non-existent user"""
        response = self.app.get('/volunteer/nonexistent_user/history')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')

    def test_add_volunteer_event(self):
        """Test adding a new event to volunteer history"""
        new_event = {
            'eventName': 'Charity Run',
            'description': 'Assisted with registration',
            'location': 'Austin, TX',
            'requiredSkills': ['Registration Management'],
            'urgency': 'medium',
            'eventDate': '2024-03-15T10:00:00.000Z',
            'participationStatus': 'registered'
        }

        response = self.app.post(
            f'/volunteer/{self.sample_user["username"]}/history',
            data=json.dumps(new_event),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        # Verify response structure
        self.assertIn('username', data)
        self.assertIn('history', data)
        self.assertEqual(len(data['history']), 2)
        
        # Verify the new event details
        added_event = data['history'][-1]
        self.assertEqual(added_event['eventName'], 'Charity Run')
        self.assertEqual(added_event['location'], 'Austin, TX')
        self.assertIsInstance(added_event['requiredSkills'], list)

    def test_add_event_to_nonexistent_user(self):
        """Test adding an event to a non-existent user's history"""
        new_event = {
            'eventName': 'Charity Run',
            'description': 'Assisted with registration',
            'location': 'Austin, TX',
            'requiredSkills': ['Registration Management'],
            'urgency': 'medium',
            'eventDate': '2024-03-15T10:00:00.000Z',
            'participationStatus': 'registered'
        }

        response = self.app.post(
            '/volunteer/nonexistent_user/history',
            data=json.dumps(new_event),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')

    def test_get_empty_history(self):
        """Test fetching history for a user with no events"""
        # Create a new user with no history
        new_user = {
            'username': 'new_user',
            'email': 'new@example.com',
            'password': 'password123',
            'skills': [],
            'preferences': '',
            'history': []
        }
        db['users'].append(new_user)

        response = self.app.get('/volunteer/new_user/history')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'new_user')
        self.assertEqual(len(data['history']), 0)

if __name__ == '__main__':
    unittest.main()