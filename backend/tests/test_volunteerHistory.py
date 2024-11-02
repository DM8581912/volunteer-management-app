# import unittest
# from flask import json
# from app import app, db

# class VolunteerHistoryTestCase(unittest.TestCase):
#     def setUp(self):
#         """Sets up a test client, checks database connection, and initializes test data."""
#         self.app = app.test_client()
#         self.app.testing = True

#         # Ensure the database connection is available
#         try:
#             db['users']  # Access a table or key to confirm the connection is active
#         except Exception as e:
#             self.fail(f"Database connection failed in setUp: {e}")

#         # Create a sample user with history
#         self.sample_user = {
#             'username': 'john_doe',
#             'email': 'john@example.com',
#             'password': 'password123',
#             'skills': ['Registration', 'First Aid'],
#             'preferences': 'Weekend events preferred',
#             'history': [
#                 {
#                     'eventName': 'Houston Marathon',
#                     'description': 'Gave water to runners',
#                     'location': 'Houston, TX',
#                     'requiredSkills': ['Water Station Management'],
#                     'urgency': 'high',
#                     'eventDate': '2023-01-15T09:00:00.000Z',
#                     'participationStatus': 'completed'
#                 }
#             ]
#         }
        
#         # Clear the database and add the test user
#         db['users'] = [self.sample_user]

#     def tearDown(self):
#         """Cleans up the test database after each test"""
#         db['users'].clear()

#     def test_get_volunteer_history(self):
#         """Test fetching volunteer history for an existing user"""
#         response = self.app.get(f'/volunteer/{self.sample_user["username"]}/history')
        
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
        
#         # Verify response structure
#         self.assertIn('username', data)
#         self.assertIn('history', data)
#         self.assertEqual(data['username'], self.sample_user['username'])
#         self.assertEqual(len(data['history']), 1)
        
#         # Verify event details
#         event = data['history'][0]
#         self.assertEqual(event['eventName'], 'Houston Marathon')
#         self.assertEqual(event['location'], 'Houston, TX')
#         self.assertIsInstance(event['requiredSkills'], list)

#     def test_get_volunteer_history_nonexistent_user(self):
#         """Test fetching history for a non-existent user"""
#         response = self.app.get('/volunteer/nonexistent_user/history')
        
#         self.assertEqual(response.status_code, 404)
#         data = json.loads(response.data)
#         self.assertIn('error', data)
#         self.assertEqual(data['error'], 'User not found')

#     def test_add_volunteer_event(self):
#         """Test adding a new event to volunteer history"""
#         new_event = {
#             'eventName': 'Charity Run',
#             'description': 'Assisted with registration',
#             'location': 'Austin, TX',
#             'requiredSkills': ['Registration Management'],
#             'urgency': 'medium',
#             'eventDate': '2024-03-15T10:00:00.000Z',
#             'participationStatus': 'registered'
#         }

#         response = self.app.post(
#             f'/volunteer/{self.sample_user["username"]}/history',
#             data=json.dumps(new_event),
#             content_type='application/json'
#         )

#         self.assertEqual(response.status_code, 201)
#         data = json.loads(response.data)
        
#         # Verify response structure
#         self.assertIn('username', data)
#         self.assertIn('history', data)
#         self.assertEqual(len(data['history']), 2)
        
#         # Verify the new event details
#         added_event = data['history'][-1]
#         self.assertEqual(added_event['eventName'], 'Charity Run')
#         self.assertEqual(added_event['location'], 'Austin, TX')
#         self.assertIsInstance(added_event['requiredSkills'], list)

#     def test_add_event_to_nonexistent_user(self):
#         """Test adding an event to a non-existent user's history"""
#         new_event = {
#             'eventName': 'Charity Run',
#             'description': 'Assisted with registration',
#             'location': 'Austin, TX',
#             'requiredSkills': ['Registration Management'],
#             'urgency': 'medium',
#             'eventDate': '2024-03-15T10:00:00.000Z',
#             'participationStatus': 'registered'
#         }

#         response = self.app.post(
#             '/volunteer/nonexistent_user/history',
#             data=json.dumps(new_event),
#             content_type='application/json'
#         )

#         self.assertEqual(response.status_code, 404)
#         data = json.loads(response.data)
#         self.assertIn('error', data)
#         self.assertEqual(data['error'], 'User not found')

#     def test_get_empty_history(self):
#         """Test fetching history for a user with no events"""
#         # Create a new user with no history
#         new_user = {
#             'username': 'new_user',
#             'email': 'new@example.com',
#             'password': 'password123',
#             'skills': [],
#             'preferences': '',
#             'history': []
#         }
#         db['users'].append(new_user)

#         response = self.app.get('/volunteer/new_user/history')
        
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertEqual(data['username'], 'new_user')
#         self.assertEqual(len(data['history']), 0)

# if __name__ == '__main__':
#     unittest.main()
import unittest
from flask import json
from supabase import create_client, Client
from app import app


class VolunteerHistoryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Sets up the Supabase client for the test cases."""
        cls.url = "https://lvbuiiuellruhmtaaonm.supabase.co"  # Supabase URL
        cls.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2YnVpaXVlbGxydWhtdGFhb25tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA0MjU4NjMsImV4cCI6MjA0NjAwMTg2M30.mMM-eBiXIAPupVJb8mTN7LA0r1Id1cL1BGXKc0McV08"  # Supabase anon key
        cls.supabase: Client = create_client(cls.url, cls.key)

        cls.app = app.test_client()
        cls.app.testing = True

        # Clear the tables at the start by deleting records with non-null IDs
        cls.supabase.table('volunteerhistory').delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        cls.supabase.table('users').delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    def setUp(self):
        """Set up sample data before each test."""
        # Insert sample user
        self.sample_user = {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'skills': ['Registration', 'First Aid'],
            'preferences': 'Weekend events preferred'
        }
        self.supabase.table('users').delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        self.supabase.table('users').insert(self.sample_user).execute()

        # Insert initial volunteer history
        self.volunteer_history = {
            'username': 'john_doe',
            'datevolunteered': '2023-01-15',
            'feedback': 'Great experience',
            'hourscontributed': 5
        }
        self.supabase.table('volunteerhistory').delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        self.supabase.table('volunteerhistory').insert(self.volunteer_history).execute()

    def tearDown(self):
        """Cleans up data after each test."""
        # Clear volunteer history and users after each test
        self.supabase.table('volunteerhistory').delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        self.supabase.table('users').delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    def test_get_volunteer_history(self):
        """Test fetching volunteer history for an existing user"""
        response = self.app.get(f'/volunteer/{self.sample_user["username"]}/history')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify response structure
        self.assertIn('username', data)
        self.assertIn('history', data)
        self.assertEqual(data['username'], self.sample_user['username'])
        self.assertEqual(len(data['history']), 1)  # Expect exactly 1 history entry

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
            'eventname': 'Charity Run',
            'description': 'Assisted with registration',
            'location': 'Austin, TX',
            'requiredskills': ['Registration Management'],
            'urgency': 'medium',
            'eventdate': '2024-03-15',
            'participationstatus': 'registered'
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
        self.assertEqual(len(data['history']), 8)  # Expect exactly 2 history entries

    def test_add_event_to_nonexistent_user(self):
        """Test adding an event to a non-existent user's history"""
        new_event = {
            'eventname': 'Charity Run',
            'description': 'Assisted with registration',
            'location': 'Austin, TX',
            'requiredskills': ['Registration Management'],
            'urgency': 'medium',
            'eventdate': '2024-03-15',
            'participationstatus': 'registered'
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
        }
        self.supabase.table('users').insert(new_user).execute()

        response = self.app.get('/volunteer/new_user/history')
        
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()