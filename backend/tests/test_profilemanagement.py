import unittest
from app import app

class TestUserProfileManagement(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

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
