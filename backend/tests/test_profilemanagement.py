import unittest
from app import app, users
import bcrypt

class TestUserProfileManagement(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        password = 'password123'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        self.user_data = {
            'username': 'testuser',
            'password': hashed_password,
            'email': 'testuser@example.com',
            'skills': ['coding'],
            'preferences': 'weekends'
        }
        users.append(self.user_data)  

    def tearDown(self):
        users.clear()  

    def test_get_profile(self):
        response = self.app.get('/profile/testuser')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'email', response.data)

    def test_update_profile(self):
        response = self.app.put('/profile/testuser', json={'email': 'newemail@example.com', 'skills': ['coding']})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile updated successfully', response.data)

if __name__ == '__main__':
    unittest.main()
