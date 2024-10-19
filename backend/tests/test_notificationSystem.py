import unittest
import json
from datetime import datetime, timedelta
from app import app, db, create_notification, check_upcoming_events

class NotificationSystemTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and initialize test data"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Clear the database
        db['users'] = []
        db['events'] = []
        db['notifications'] = {}
        
        # Create test users
        self.test_user = {
            'username': 'test_user',
            'email': 'test@example.com',
            'password': 'password123',
            'skills': ['First Aid', 'Heavy Lifting'],
            'preferences': 'Weekend events'
        }
        db['users'].append(self.test_user)

        # Create test event
        self.test_event = {
            'eventName': 'Emergency Response',
            'location': 'Downtown Houston',
            'requiredSkills': ['First Aid'],
            'urgency': 'high',
            'eventDate': (datetime.now() + timedelta(days=1)).isoformat()
        }
        db['events'].append(self.test_event)

    def tearDown(self):
        """Clean up after each test"""
        db['users'].clear()
        db['events'].clear()
        db['notifications'].clear()

    def test_create_notification(self):
        """Test creating a new notification"""
        notification = create_notification(
            'test_user',
            'Test notification message',
            'general',
            'test_id'
        )
        
        self.assertIn('test_user', db['notifications'])
        self.assertEqual(len(db['notifications']['test_user']), 1)
        self.assertEqual(notification['message'], 'Test notification message')
        self.assertEqual(notification['type'], 'general')
        self.assertEqual(notification['related_id'], 'test_id')
        self.assertFalse(notification['read'])

    def test_get_user_notifications(self):
        """Test retrieving user notifications"""
        # Create multiple notifications
        create_notification('test_user', 'Notification 1', 'general', 'id1')
        create_notification('test_user', 'Notification 2', 'event_match', 'id2')
        
        response = self.app.get('/notifications/test_user')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('notifications', data)
        self.assertEqual(len(data['notifications']), 2)
        
        # Verify notification details
        notifications = data['notifications']
        self.assertEqual(notifications[0]['message'], 'Notification 1')
        self.assertEqual(notifications[1]['message'], 'Notification 2')

    def test_mark_notifications_read(self):
        """Test marking notifications as read"""
        # Create notifications
        create_notification('test_user', 'Notification 1', 'general', 'id1')
        create_notification('test_user', 'Notification 2', 'event_match', 'id2')
        
        # Get notification IDs
        notification_ids = [n['id'] for n in db['notifications']['test_user']]
        
        # Mark notifications as read
        response = self.app.post(
            '/notifications/test_user/mark-read',
            data=json.dumps({'notification_ids': notification_ids}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify notifications are marked as read
        for notification in db['notifications']['test_user']:
            self.assertTrue(notification['read'])

    def test_event_match_notification(self):
        """Test notification creation for matching events"""
        event_data = {
            'eventName': 'First Aid Training',
            'location': 'Medical Center',
            'requiredSkills': ['First Aid'],
            'urgency': 'medium',
            'eventDate': '2024-12-01T10:00:00.000Z'
        }
        
        # Create event via API
        response = self.app.post(
            '/eventform',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Verify notification was created for matching user
        self.assertIn('test_user', db['notifications'])
        notifications = db['notifications']['test_user']
        self.assertTrue(any(
            n['type'] == 'event_match' and 'First Aid Training' in n['message']
            for n in notifications
        ))

    def test_event_reminder_notification(self):
        """Test notification creation for upcoming event reminders"""
        tomorrow_event = {
            'eventName': 'Tomorrow Event',
            'location': 'City Center',
            'requiredSkills': ['Heavy Lifting'],
            'urgency': 'high',
            'eventDate': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        }
        db['events'].append(tomorrow_event)
        
        # Manually trigger the reminder check
        from app import check_upcoming_events
        check_upcoming_events(test_mode=True)  # Call with test_mode=True
        
        # Verify reminder notification was created
        self.assertIn('test_user', db['notifications'])
        notifications = db['notifications']['test_user']
        self.assertTrue(any(
            n['type'] == 'event_reminder' and 'Tomorrow Event' in n['message']
            for n in notifications
        ))


    def test_get_notifications_nonexistent_user(self):
        """Test getting notifications for non-existent user"""
        response = self.app.get('/notifications/nonexistent_user')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('notifications', data)
        self.assertEqual(len(data['notifications']), 0)

    def test_mark_nonexistent_notifications_read(self):
        """Test marking non-existent notifications as read"""
        response = self.app.post(
            '/notifications/test_user/mark-read',
            data=json.dumps({'notification_ids': [999]}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
