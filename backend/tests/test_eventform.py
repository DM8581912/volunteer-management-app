# import unittest
# import json
# from app import app

# class EventFormTestCase(unittest.TestCase):

#     def setUp(self):
#         """Set up a test client for Flask"""
#         self.app = app.test_client()
#         self.app.testing = True

#     def test_eventform_post_success(self):
#         """Test successful event form submission"""
#         event_data = {
#             "eventName": "Cleaning Event",
#             "location": "Houston, Texas",
#             "urgency": "medium",
#             "requiredSkills": ["Carry over 50 lbs"],
#             "eventDate": "2024-10-17T22:24:54.000Z"
#         }

#         response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')
        
#         # Assert response status code is 201 (Created)
#         self.assertEqual(response.status_code, 201)

#         # Assert response structure matches backend
#         response_json = json.loads(response.data)
#         self.assertIn('message', response_json)
#         self.assertEqual(response_json['message'], 'Event created successfully')
#         self.assertIn('event', response_json)
#         self.assertIn('matches', response_json)

#         # Verify event data was stored correctly
#         created_event = response_json['event']
#         self.assertEqual(created_event['eventName'], event_data['eventName'])
#         self.assertEqual(created_event['location'], event_data['location'])
#         self.assertEqual(created_event['urgency'], event_data['urgency'])
#         self.assertEqual(created_event['requiredSkills'], event_data['requiredSkills'])
#         self.assertEqual(created_event['eventDate'], event_data['eventDate'])

#     def test_eventform_post_missing_event_name(self):
#         """Test form submission with missing event_name"""
#         event_data = {
#             "location": "Houston, Texas",
#             "urgency": "medium",
#             "requiredSkills": ["Carry over 50 lbs"],
#             "eventDate": "2024-10-17T22:24:54.000Z"
#         }

#         response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

#         self.assertEqual(response.status_code, 400)
#         response_json = json.loads(response.data)
#         self.assertIn('error', response_json)
#         self.assertIn('eventName is required', response_json['error'][0])

#     def test_eventform_post_missing_event_date(self):
#         """Test form submission with missing event_date"""
#         event_data = {
#             "eventName": "Cleaning Event",
#             "location": "Houston, Texas",
#             "urgency": "medium",
#             "requiredSkills": ["Carry over 50 lbs"]
#         }

#         response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

#         self.assertEqual(response.status_code, 400)
#         response_json = json.loads(response.data)
#         self.assertIn('error', response_json)
#         self.assertIn('eventDate is required', response_json['error'][0])

#     def test_eventform_post_invalid_urgency(self):
#         """Test form submission with invalid urgency"""
#         event_data = {
#             "eventName": "Cleaning Event",
#             "location": "Houston, Texas",
#             "urgency": "invalid",
#             "requiredSkills": ["Carry over 50 lbs"],
#             "eventDate": "2024-10-17T22:24:54.000Z"
#         }

#         response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

#         self.assertEqual(response.status_code, 400)
#         response_json = json.loads(response.data)
#         self.assertIn('error', response_json)
#         self.assertIn('urgency must be one of: low, medium, high', response_json['error'][0])

#     def test_eventform_post_missing_required_skills(self):
#         """Test form submission with missing requiredSkills"""
#         event_data = {
#             "eventName": "Cleaning Event",
#             "location": "Houston, Texas",
#             "urgency": "medium",
#             "eventDate": "2024-10-17T22:24:54.000Z"
#         }

#         response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

#         self.assertEqual(response.status_code, 400)
#         response_json = json.loads(response.data)
#         self.assertIn('error', response_json)
#         self.assertIn('requiredSkills is required', response_json['error'][0])

#     def test_eventform_post_short_event_name(self):
#         """Test form submission with too short event name"""
#         event_data = {
#             "eventName": "Test",  # Less than 5 characters
#             "location": "Houston, Texas",
#             "urgency": "medium",
#             "requiredSkills": ["Carry over 50 lbs"],
#             "eventDate": "2024-10-17T22:24:54.000Z"
#         }

#         response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

#         self.assertEqual(response.status_code, 400)
#         response_json = json.loads(response.data)
#         self.assertIn('error', response_json)
#         self.assertIn('eventName must be at least 5 characters', response_json['error'][0])

#     def test_eventform_get(self):
#         """Test getting all events"""
#         response = self.app.get('/eventform')
        
#         self.assertEqual(response.status_code, 200)
#         response_json = json.loads(response.data)
#         self.assertIn('events', response_json)
#         self.assertIsInstance(response_json['events'], list)

# if __name__ == '__main__':
#     unittest.main()

import unittest
import json
from dotenv import load_dotenv
import os
import datetime

# Load environment variables explicitly for testing
load_dotenv()

from app import app, supabase  # Import app and supabase after loading environment variables

class EventFormTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a test client for Flask and check Supabase connectivity"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Check Supabase connectivity
        response = supabase.table('events').select('*').limit(1).execute()
        print("Connection test response:", response)
        assert response.data is not None, "Supabase connection failed"

        # Sample event data to test retrieval
        self.sample_event_data = {
            "eventName": "Sample Event",
            "location": "Austin, Texas",
            "urgency": "high",
            "requiredSkills": ["Teamwork", "Lifting"],
            "eventDate": "2024-10-17"
        }
        self.insert_sample_event()

    def tearDown(self):
        """Clean up database after each test"""
        supabase.table('events').delete().eq('eventName', self.sample_event_data['eventName']).execute()

    def insert_sample_event(self):
        """Helper function to insert a sample event directly into the database"""
        response = supabase.table('events').insert(self.sample_event_data).execute()
        assert response.data is not None, "Failed to insert sample event"

    def test_eventform_post_success(self):
        """Test successful event form submission"""
        event_data = {
            "eventName": "Cleaning Event",
            "location": "Houston, Texas",
            "urgency": "medium",
            "requiredSkills": ["Carry over 50 lbs"],
            "eventDate": "2024-10-17"
        }
        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')
        self.assertEqual(response.status_code, 201, "Expected 201 status code for successful event submission.")

        response_json = json.loads(response.data)
        self.assertIn('message', response_json)
        self.assertEqual(response_json['message'], 'Event created successfully')
        self.assertIn('event', response_json)

        # Verify event was added to the database
        db_response = supabase.table('events').select('*').eq('eventName', event_data['eventName']).execute()
        self.assertEqual(len(db_response.data), 1)
        created_event = db_response.data[0]
        self.assertEqual(created_event['eventName'], event_data['eventName'])
        self.assertEqual(created_event['location'], event_data['location'])

    def test_eventform_get_from_db(self):
        """Test retrieving events directly from the database"""
        response = self.app.get('/eventform')
        self.assertEqual(response.status_code, 200, "Expected 200 status code for retrieving events.")
        
        response_json = json.loads(response.data)
        self.assertIn('events', response_json)
        self.assertIsInstance(response_json['events'], list)
        
        # Check if the sample event is in the list
        events = response_json['events']
        event_names = [event['eventName'] for event in events]
        self.assertIn(self.sample_event_data['eventName'], event_names)

    def test_db_insert_event_with_missing_field(self):
        """Test database-level validation for missing fields"""
        incomplete_event = {
            "eventName": "Incomplete Event",
            "urgency": "high",
            "eventDate": "2024-10-17"
            # Missing 'location' and 'requiredSkills'
        }
        try:
            response = supabase.table('events').insert(incomplete_event).execute()
            self.fail("Insert should fail due to missing fields, but it succeeded.")
        except Exception as e:
            self.assertIn("null value in column", str(e), "Expected not-null constraint error for missing fields.")

    def test_db_insert_event_with_invalid_date(self):
        """Test database-level validation with an invalid event date"""
        invalid_event = {
            "eventName": "Invalid Date Event",
            "location": "Houston, Texas",
            "urgency": "medium",
            "requiredSkills": ["Teamwork"],
            "eventDate": "invalid-date"  # Incorrect date format
        }
        try:
            response = supabase.table('events').insert(invalid_event).execute()
            self.fail("Insert should fail due to invalid date, but it succeeded.")
        except Exception as e:
            self.assertIn("invalid input syntax for type date", str(e), "Expected date format error.")

    def test_db_delete_event(self):
        """Test deletion of an event from the database"""
        event_name = self.sample_event_data['eventName']
        # Delete the sample event from the database
        delete_response = supabase.table('events').delete().eq('eventName', event_name).execute()
        
        # Verify the event no longer exists in the database
        fetch_response = supabase.table('events').select('*').eq('eventName', event_name).execute()
        self.assertEqual(len(fetch_response.data), 0, "Event was not deleted successfully")

if __name__ == '__main__':
    unittest.main()



