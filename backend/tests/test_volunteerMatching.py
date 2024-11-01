# import unittest
# import json
# from app import app, db, calculate_match_score, find_best_matches
# import bcrypt
# import pytest
# from supabase import create_client
# import os


# class VolunteerMatchingTestCase(unittest.TestCase):
#     def setUp(self):
#         """Set up test client and initialize test data"""
#         self.app = app.test_client()
#         self.app.testing = True
        
#         # Clear the database
#         db['users'] = []
#         db['events'] = []
        
#         # Create test users with various skills
#         self.test_users = [
#             {
#                 'username': 'first_aid_expert',
#                 'email': 'first.aid@example.com',
#                 'password': 'password123',
#                 'skills': ['First Aid', 'CPR', 'Emergency Response'],
#                 'preferences': 'Medical events'
#             },
#             {
#                 'username': 'tech_volunteer',
#                 'email': 'tech@example.com',
#                 'password': 'password123',
#                 'skills': ['Computer Repair', 'Teaching', 'Documentation'],
#                 'preferences': 'Technology events'
#             },
#             {
#                 'username': 'general_helper',
#                 'email': 'helper@example.com',
#                 'password': 'password123',
#                 'skills': ['Heavy Lifting', 'First Aid', 'Driving'],
#                 'preferences': 'Any events'
#             }
#         ]
#         db['users'].extend(self.test_users)
        
#         # Create test events
#         self.test_events = [
#             {
#                 'eventName': 'Medical Training',
#                 'location': 'Hospital',
#                 'requiredSkills': ['First Aid', 'CPR'],
#                 'urgency': 'high',
#                 'eventDate': '2024-12-01T10:00:00.000Z'
#             },
#             {
#                 'eventName': 'Computer Workshop',
#                 'location': 'Community Center',
#                 'requiredSkills': ['Computer Repair', 'Teaching'],
#                 'urgency': 'medium',
#                 'eventDate': '2024-12-02T10:00:00.000Z'
#             }
#         ]
#         db['events'].extend(self.test_events)

#     def tearDown(self):
#         """Clean up after each test"""
#         db['users'].clear()
#         db['events'].clear()

#     def test_calculate_match_score(self):
#         """Test the match score calculation function"""
#         # Test perfect match
#         score = calculate_match_score(
#             ['First Aid', 'CPR'],
#             ['First Aid', 'CPR']
#         )
#         self.assertEqual(score, 100)
        
#         # Test partial match
#         score = calculate_match_score(
#             ['First Aid', 'CPR', 'Driving'],
#             ['First Aid', 'CPR']
#         )
#         self.assertEqual(score, 100)
        
#         # Test partial skills match
#         score = calculate_match_score(
#             ['First Aid'],
#             ['First Aid', 'CPR']
#         )
#         self.assertEqual(score, 50)
        
#         # Test no match
#         score = calculate_match_score(
#             ['Cooking'],
#             ['First Aid', 'CPR']
#         )
#         self.assertEqual(score, 0)

#     def test_find_best_matches(self):
#         """Test finding best matches for an event"""
#         medical_event = self.test_events[0]
#         matches = find_best_matches(medical_event)
        
#         # Should find at least two matches (first_aid_expert and general_helper)
#         # self.assertGreaterEqual(len(matches), 2)
        
#         # First match should be first_aid_expert (has more matching skills)
#         self.assertEqual(matches[0]['username'], 'first_aid_expert')
#         self.assertEqual(matches[0]['score'], 100)

#     def test_get_event_matches_api(self):
#         """Test getting matches for an event via API"""
#         response = self.app.get('/matches/event/Medical Training')
        
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertIn('matches', data)
#         matches = data['matches']
        
#         # Verify matches are returned in correct order
#         self.assertGreater(len(matches), 0)
#         self.assertEqual(matches[0]['username'], 'first_aid_expert')

#     def test_get_volunteer_matches_api(self):
#         """Test getting matching events for a volunteer via API"""
#         response = self.app.get('/matches/volunteer/first_aid_expert')
        
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.data)
#         self.assertIn('matches', data)
#         matches = data['matches']
        
#         # Should match medical training event
#         self.assertEqual(len(matches), 1)
#         self.assertEqual(matches[0]['event']['eventName'], 'Medical Training')
#         self.assertIn('matchScore', matches[0])

#     def test_nonexistent_event_matches(self):
#         """Test getting matches for non-existent event"""
#         response = self.app.get('/matches/event/NonexistentEvent')
        
#         self.assertEqual(response.status_code, 404)
#         data = json.loads(response.data)
#         self.assertIn('error', data)

#     def test_nonexistent_volunteer_matches(self):
#         """Test getting matches for non-existent volunteer"""
#         response = self.app.get('/matches/volunteer/nonexistent_user')
        
#         self.assertEqual(response.status_code, 404)
#         data = json.loads(response.data)
#         self.assertIn('error', data)

#     def test_create_event_with_matches(self):
#         """Test match creation when new event is created"""
#         new_event = {
#             'eventName': 'Emergency Response Training',
#             'location': 'Fire Station',
#             'requiredSkills': ['First Aid', 'Emergency Response'],
#             'urgency': 'high',
#             'eventDate': '2024-12-03T10:00:00.000Z'
#         }
        
#         response = self.app.post(
#             '/eventform',
#             data=json.dumps(new_event),
#             content_type='application/json'
#         )
        
#         self.assertEqual(response.status_code, 201)
#         data = json.loads(response.data)
        
#         # Verify matches were found
#         self.assertIn('matches', data)
#         matches = data['matches']
#         self.assertGreater(len(matches), 0)
        
#         # first_aid_expert should be the best match
#         self.assertEqual(matches[0]['username'], 'first_aid_expert')
#         self.assertEqual(matches[0]['score'], 100)

#     def test_match_score_edge_cases(self):
#         """Test match score calculation edge cases"""
#         # Empty skills lists
#         score = calculate_match_score([], [])
#         self.assertEqual(score, 0)
        
#         # None values
#         score = calculate_match_score(None, ['First Aid'])
#         self.assertEqual(score, 0)
        
#         score = calculate_match_score(['First Aid'], None)
#         self.assertEqual(score, 0)
        
#         # Case sensitivity
#         score = calculate_match_score(
#             ['first aid', 'CPR'],
#             ['First Aid', 'CPR']
#         )
#         self.assertEqual(score, 100)

# if __name__ == '__main__':
#     unittest.main()
import unittest
import json
from app import app, db, calculate_match_score, find_best_matches
from supabase import create_client
from unittest.mock import MagicMock

class VolunteerMatchingTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and initialize test data"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Mocking the Supabase client
        self.supabase_client = create_client('url', 'key')
        db['supabase'] = self.supabase_client
        
        # Clear the database
        db['users'] = []
        db['events'] = []
        
        # Create test users with various skills
        self.test_users = [
            {
                'username': 'first_aid_expert',
                'email': 'first.aid@example.com',
                'password': 'password123',
                'skills': ['First Aid', 'CPR', 'Emergency Response'],
                'preferences': 'Medical events'
            },
            {
                'username': 'tech_volunteer',
                'email': 'tech@example.com',
                'password': 'password123',
                'skills': ['Computer Repair', 'Teaching', 'Documentation'],
                'preferences': 'Technology events'
            },
            {
                'username': 'general_helper',
                'email': 'helper@example.com',
                'password': 'password123',
                'skills': ['Heavy Lifting', 'First Aid', 'Driving'],
                'preferences': 'Any events'
            }
        ]
        db['users'].extend(self.test_users)
        
        # Create test events
        self.test_events = [
            {
                'eventName': 'Medical Training',
                'location': 'Hospital',
                'requiredSkills': ['First Aid', 'CPR'],
                'urgency': 'high',
                'eventDate': '2024-12-01T10:00:00.000Z'
            },
            {
                'eventName': 'Computer Workshop',
                'location': 'Community Center',
                'requiredSkills': ['Computer Repair', 'Teaching'],
                'urgency': 'medium',
                'eventDate': '2024-12-02T10:00:00.000Z'
            }
        ]
        db['events'].extend(self.test_events)

    def tearDown(self):
        """Clean up after each test"""
        db['users'].clear()
        db['events'].clear()

    def test_calculate_match_score(self):
        """Test the match score calculation function"""
        # Test perfect match
        score = calculate_match_score(
            ['First Aid', 'CPR'],
            ['First Aid', 'CPR']
        )
        self.assertEqual(score, 100)
        
        # Test partial match
        score = calculate_match_score(
            ['First Aid', 'CPR', 'Driving'],
            ['First Aid', 'CPR']
        )
        self.assertEqual(score, 100)
        
        # Test partial skills match
        score = calculate_match_score(
            ['First Aid'],
            ['First Aid', 'CPR']
        )
        self.assertEqual(score, 50)
        
        # Test no match
        score = calculate_match_score(
            ['Cooking'],
            ['First Aid', 'CPR']
        )
        self.assertEqual(score, 0)

    def test_find_best_matches(self):
        """Test finding best matches for an event"""
        medical_event = self.test_events[0]
        matches = find_best_matches(medical_event)
        
        # Should find at least two matches (first_aid_expert and general_helper)
        self.assertGreaterEqual(len(matches), 2)
        
        # First match should be first_aid_expert (has more matching skills)
        self.assertEqual(matches[0]['username'], 'first_aid_expert')
        self.assertEqual(matches[0]['score'], 100)

    def test_get_event_matches_api(self):
        """Test getting matches for an event via API"""
        response = self.app.get('/matches/event/Medical Training')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('matches', data)
        matches = data['matches']
        
        # Verify matches are returned in correct order
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0]['username'], 'first_aid_expert')

    def test_get_volunteer_matches_api(self):
        """Test getting matching events for a volunteer via API"""
        response = self.app.get('/matches/volunteer/first_aid_expert')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('matches', data)
        matches = data['matches']
        
        # Should match medical training event
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['event']['eventName'], 'Medical Training')
        self.assertIn('matchScore', matches[0])

    def test_nonexistent_event_matches(self):
        """Test getting matches for non-existent event"""
        response = self.app.get('/matches/event/NonexistentEvent')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_nonexistent_volunteer_matches(self):
        """Test getting matches for non-existent volunteer"""
        response = self.app.get('/matches/volunteer/nonexistent_user')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_create_event_with_matches(self):
        """Test match creation when new event is created"""
        new_event = {
            'eventName': 'Emergency Response Training',
            'location': 'Fire Station',
            'requiredSkills': ['First Aid', 'Emergency Response'],
            'urgency': 'high',
            'eventDate': '2024-12-03T10:00:00.000Z'
        }
        
        response = self.app.post(
            '/eventform',
            data=json.dumps(new_event),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        # Verify matches were found
        self.assertIn('matches', data)
        matches = data['matches']
        self.assertGreater(len(matches), 0)
        
        # first_aid_expert should be the best match
        self.assertEqual(matches[0]['username'], 'first_aid_expert')
        self.assertEqual(matches[0]['score'], 100)

    def test_match_score_edge_cases(self):
        """Test match score calculation edge cases"""
        # Empty skills lists
        score = calculate_match_score([], [])
        self.assertEqual(score, 0)
        
        # None values
        score = calculate_match_score(None, ['First Aid'])
        self.assertEqual(score, 0)
        
        score = calculate_match_score(['First Aid'], None)
        self.assertEqual(score, 0)
        
        # Case sensitivity
        score = calculate_match_score(
            ['first aid', 'CPR'],
            ['First Aid', 'CPR']
        )
        self.assertEqual(score, 100)

if __name__ == '__main__':
    unittest.main()
