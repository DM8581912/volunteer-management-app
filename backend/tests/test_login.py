import unittest
from backend.app import app, users  
import bcrypt

class TestLogin(unittest.TestCase):

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

    def test_valid_login(self):
        response = self.app.post('/login', json={'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful', response.data)

    def test_invalid_login(self):
        response = self.app.post('/login', json={'username': 'wronguser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid credentials', response.data)

if __name__ == '__main__':
    unittest.main()
