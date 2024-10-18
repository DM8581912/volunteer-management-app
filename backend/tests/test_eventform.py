import unittest
import json
from app import app

class EventFormTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a test client for Flask"""
        self.app = app.test_client()
        self.app.testing = True

    def test_eventform_post_success(self):
        """Test successful event form submission"""
        event_data = {
            "eventName": "Cleaning Event",
            "location": "Houston, Texas",
            "urgency": "medium",
            "requiredSkills": ["Carry over 50 lbs"],
            "eventDate": "2024-10-17T22:24:54.000Z"
        }

        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')
        
        # Assert response status code is 201 (Created)
        self.assertEqual(response.status_code, 201)

        # Assert response structure matches backend
        response_json = json.loads(response.data)
        self.assertIn('message', response_json)
        self.assertEqual(response_json['message'], 'Event created successfully')
        self.assertIn('event', response_json)
        self.assertIn('matches', response_json)

        # Verify event data was stored correctly
        created_event = response_json['event']
        self.assertEqual(created_event['eventName'], event_data['eventName'])
        self.assertEqual(created_event['location'], event_data['location'])
        self.assertEqual(created_event['urgency'], event_data['urgency'])
        self.assertEqual(created_event['requiredSkills'], event_data['requiredSkills'])
        self.assertEqual(created_event['eventDate'], event_data['eventDate'])

    def test_eventform_post_missing_event_name(self):
        """Test form submission with missing event_name"""
        event_data = {
            "location": "Houston, Texas",
            "urgency": "medium",
            "requiredSkills": ["Carry over 50 lbs"],
            "eventDate": "2024-10-17T22:24:54.000Z"
        }

        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data)
        self.assertIn('error', response_json)
        self.assertIn('eventName is required', response_json['error'][0])

    def test_eventform_post_missing_event_date(self):
        """Test form submission with missing event_date"""
        event_data = {
            "eventName": "Cleaning Event",
            "location": "Houston, Texas",
            "urgency": "medium",
            "requiredSkills": ["Carry over 50 lbs"]
        }

        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data)
        self.assertIn('error', response_json)
        self.assertIn('eventDate is required', response_json['error'][0])

    def test_eventform_post_invalid_urgency(self):
        """Test form submission with invalid urgency"""
        event_data = {
            "eventName": "Cleaning Event",
            "location": "Houston, Texas",
            "urgency": "invalid",
            "requiredSkills": ["Carry over 50 lbs"],
            "eventDate": "2024-10-17T22:24:54.000Z"
        }

        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data)
        self.assertIn('error', response_json)
        self.assertIn('urgency must be one of: low, medium, high', response_json['error'][0])

    def test_eventform_post_missing_required_skills(self):
        """Test form submission with missing requiredSkills"""
        event_data = {
            "eventName": "Cleaning Event",
            "location": "Houston, Texas",
            "urgency": "medium",
            "eventDate": "2024-10-17T22:24:54.000Z"
        }

        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data)
        self.assertIn('error', response_json)
        self.assertIn('requiredSkills is required', response_json['error'][0])

    def test_eventform_post_short_event_name(self):
        """Test form submission with too short event name"""
        event_data = {
            "eventName": "Test",  # Less than 5 characters
            "location": "Houston, Texas",
            "urgency": "medium",
            "requiredSkills": ["Carry over 50 lbs"],
            "eventDate": "2024-10-17T22:24:54.000Z"
        }

        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data)
        self.assertIn('error', response_json)
        self.assertIn('eventName must be at least 5 characters', response_json['error'][0])

    def test_eventform_get(self):
        """Test getting all events"""
        response = self.app.get('/eventform')
        
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertIn('events', response_json)
        self.assertIsInstance(response_json['events'], list)

if __name__ == '__main__':
    unittest.main()