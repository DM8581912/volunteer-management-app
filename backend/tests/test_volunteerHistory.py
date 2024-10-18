import unittest
from flask import json
from app import app, users

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Sets up a test client
        self.app = app.test_client()
        self.app.testing = True

        # Adding a sample user for testing
        self.sample_user = {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'history': [
                {
                    'eventName': 'Houston Marathon',
                    'description': 'Gave water to runners',
                    'location': 'Houston, TX',
                    'requiredSkills': 'Water handing skills max lvl',
                    'urgency': 'Urgent',
                    'date': 'January 2023',
                    'participationStatus': 'Not Participating'
                }
            ]
        }
        users.append(self.sample_user)

    def tearDown(self):
        # Remove the test user after each test
        users.clear()

    # Test fetching volunteer history
    def test_get_volunteer_history(self):
        response = self.app.get(f'/volunteer/{self.sample_user["username"]}/history')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['username'], self.sample_user['username'])
        self.assertEqual(len(data['history']), 1)
        self.assertEqual(data['history'][0]['eventName'], 'Houston Marathon')

    # Test fetching non-existent user history
    def test_get_volunteer_history_nonexistent_user(self):
        response = self.app.get('/volunteer/nonexistent_user/history')
        self.assertEqual(response.status_code, 404)

    # Test adding an event to the volunteer history
    def test_add_volunteer_event(self):
        new_event = {
            'eventName': 'Charity Run',
            'description': 'Assisted runners with registration',
            'location': 'Austin, TX',
            'requiredSkills': 'Registration skills',
            'urgency': 'Moderate',
            'date': 'March 2024',
            'participationStatus': 'Participating'
        }

        response = self.app.post(
            f'/volunteer/{self.sample_user["username"]}/history',
            data=json.dumps(new_event),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data)
        self.assertEqual(len(data['history']), 2)  # After adding one more event
        self.assertEqual(data['history'][1]['eventName'], 'Charity Run')

    # Test adding event to non-existent user
    def test_add_event_to_nonexistent_user(self):
        new_event = {
            'eventName': 'Charity Run',
            'description': 'Assisted runners',
            'location': 'Austin, TX',
            'requiredSkills': 'Registration',
            'urgency': 'Moderate',
            'date': 'March 2024',
            'participationStatus': 'Participating'
        }

        response = self.app.post(
            '/volunteer/nonexistent_user/history',
            data=json.dumps(new_event),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
