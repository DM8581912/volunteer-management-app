import unittest
from app import app, db
import bcrypt

class TestUserProfileManagement(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        password = 'password123'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Set up the test user in the db['users'] list
        self.user_data = {
            'username': 'testuser',
            'password': hashed_password,
            'email': 'testuser@example.com',
            'skills': ['coding'],
            'preferences': 'weekends'
        }
        db['users'].append(self.user_data)  # Use db['users'] instead of users

    def tearDown(self):
        db['users'].clear()  # Clear the users in db after each test

    def test_get_profile(self):
        response = self.app.get('/profile/testuser')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'email', response.data)  # Check if 'email' is in the response

    def test_update_profile(self):
        # Add 'username' to the request body to meet validation requirements
        response = self.app.put('/profile/testuser', json={
            'username': 'testuser',  # Include the username in the request body
            'email': 'newemail@example.com',
            'skills': ['coding']
        })
        
        # Print the response for debugging purposes
        if response.status_code != 200:
            print("Response status code:", response.status_code)
            print("Response data:", response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile updated successfully', response.data)

if __name__ == '__main__':
    unittest.main()
