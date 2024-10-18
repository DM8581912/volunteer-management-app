import unittest
from app import app

class TestLogin(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

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
