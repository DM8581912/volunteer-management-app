import unittest
import json
from app import app  # Import your Flask app

class EventFormTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test client for Flask"""
        self.app = app.test_client()
        self.app.testing = True  # Enable testing mode

    def test_eventform_post_success(self):
        """Test successful event form submission"""
        event_data = {
            "event_name": "Cleaning Event",
            "event_description": "Cleaning at the park with friends.",
            "location": "Houston, Texas",
            "urgency": "medium",
            "required_skills": ["Carry over 50 lbs"],
            "event_date": "2024-10-17T22:24:54.000Z"
        }

        # Simulate a POST request to the /eventform route
        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')
        
        # Assert that the response status code is 201 (Created)
        self.assertEqual(response.status_code, 201)

        # Assert that the response contains a success message
        response_json = json.loads(response.data)
        self.assertIn('message', response_json)
        self.assertEqual(response_json['message'], 'Event created successfully')

    def test_eventform_post_missing_event_name(self):
        """Test form submission with missing event_name"""
        event_data = {
            "event_description": "Cleaning at the park with friends.",
            "location": "Houston, Texas",
            "urgency": "medium",
            "required_skills": ["Carry over 50 lbs"],
            "event_date": "2024-10-17T22:24:54.000Z"
        }

        # Simulate a POST request to the /eventform route without event_name
        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Assert that the response contains the expected validation error
        response_json = json.loads(response.data)
        self.assertIn('errors', response_json)
        self.assertIn('Event name must be at least 5 characters long.', response_json['errors'])

    def test_eventform_post_missing_event_date(self):
        """Test form submission with missing event_date"""
        event_data = {
            "event_name": "Cleaning Event",
            "event_description": "Cleaning at the park with friends.",
            "location": "Houston, Texas",
            "urgency": "medium",
            "required_skills": ["Carry over 50 lbs"]
        }

        # Simulate a POST request to the /eventform route without event_date
        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Assert that the response contains the expected validation error
        response_json = json.loads(response.data)
        self.assertIn('errors', response_json)
        self.assertIn('Event date is required.', response_json['errors'])

    def test_eventform_post_invalid_urgency(self):
        """Test form submission with invalid urgency"""
        event_data = {
            "event_name": "Cleaning Event",
            "event_description": "Cleaning at the park with friends.",
            "location": "Houston, Texas",
            "urgency": "invalid",  # Invalid urgency level
            "required_skills": ["Carry over 50 lbs"],
            "event_date": "2024-10-17T22:24:54.000Z"
        }

        # Simulate a POST request to the /eventform route with invalid urgency
        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Assert that the response contains the expected validation error
        response_json = json.loads(response.data)
        self.assertIn('errors', response_json)
        self.assertIn('Urgency must be one of the following: low, medium, high.', response_json['errors'])

    def test_eventform_post_missing_required_skills(self):
        """Test form submission with missing required_skills"""
        event_data = {
            "event_name": "Cleaning Event",
            "event_description": "Cleaning at the park with friends.",
            "location": "Houston, Texas",
            "urgency": "medium",
            "event_date": "2024-10-17T22:24:54.000Z"
        }

        # Simulate a POST request to the /eventform route without required_skills
        response = self.app.post('/eventform', data=json.dumps(event_data), content_type='application/json')

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Assert that the response contains the expected validation error
        response_json = json.loads(response.data)
        self.assertIn('errors', response_json)
        self.assertIn('At least one required skill is required.', response_json['errors'])

if __name__ == '__main__':
    unittest.main()
