from flask import Flask, request, jsonify
import bcrypt
from flask_cors import CORS
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
CORS(app, resources={r"/eventform": {"origins": "http://localhost:3000"}})

users = []

def validate_profile_data(data, update=False):
    errors = []

    if 'email' in data:
        if len(data['email']) > 50:
            errors.append('Email cannot exceed 50 characters.')
        if not isinstance(data['email'], str):
            errors.append('Email must be a string.')

    if 'skills' in data and not isinstance(data['skills'], list):
        errors.append('Skills must be a list.')

    if 'preferences' in data and not isinstance(data['preferences'], str):
        errors.append('Preferences must be a string.')

    return errors

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Volunteer Management App Backend!"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    errors = validate_profile_data(data)

    if not data.get('username'):
        errors.append('Username is required.')
    elif len(data['username']) < 3 or len(data['username']) > 30:
        errors.append('Username must be between 3 and 30 characters.')

    if not data.get('password'):
        errors.append('Password is required.')
    elif len(data['password']) < 6:
        errors.append('Password must be at least 6 characters long.')

    if not data.get('email'):
        errors.append('Email is required.')

    if errors:
        return jsonify({'errors': errors}), 400

    for user in users:
        if user['username'] == data['username']:
            return jsonify({'error': 'User already exists'}), 400

    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    user_info = {
        'username': data['username'],
        'password': hashed_password,
        'email': data['email'],
        'skills': data.get('skills', []),
        'preferences': data.get('preferences', '')
    }
    users.append(user_info)

    response_user_info = {
        'username': data['username'],
        'email': data['email'],
        'skills': data.get('skills', []),
        'preferences': data.get('preferences', '')
    }

    return jsonify({'message': 'User registered successfully', 'user': response_user_info}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json

    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    for user in users:
        if user['username'] == data['username']:
            if bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
                return jsonify({'message': 'Login successful'}), 200
            else:
                return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    for user in users:
        if user['username'] == username:
            response_user_info = {
                'username': user['username'],
                'email': user['email'],
                'skills': user['skills'],
                'preferences': user['preferences']
            }
            return jsonify({'user': response_user_info}), 200

    return jsonify({'error': 'User not found'}), 404

@app.route('/profile/<username>', methods=['PUT'])
def update_profile(username):
    data = request.json
    errors = validate_profile_data(data, update=True)

    if errors:
        return jsonify({'errors': errors}), 400

    for user in users:
        if user['username'] == username:
            user['email'] = data.get('email', user['email'])
            user['skills'] = data.get('skills', user['skills'])
            user['preferences'] = data.get('preferences', user['preferences'])

            response_user_info = {
                'username': user['username'],
                'email': user['email'],
                'skills': user['skills'],
                'preferences': user['preferences']
            }

            return jsonify({'message': 'Profile updated successfully', 'user': response_user_info}), 200

    return jsonify({'error': 'User not found'}), 404


# In-memory event storage (mock database)
events = []

# Validation for event form data
def validate_event_data(data):
    errors = []
    if 'eventName' not in data or len(data['eventName']) < 5:
        errors.append("Event name must be at least 5 characters long.")    
    if 'eventDate' not in data:
        errors.append("Event date is required.")     
    if 'urgency' not in data or data['urgency'] not in ['low', 'medium', 'high']:
        errors.append("Urgency must be low, medium, or high.")   
    # Validate requiredSkills: It must be present and contain at least one skill
    if 'requiredSkills' not in data or not isinstance(data['requiredSkills'], list) or len(data['requiredSkills']) == 0:
        errors.append("At least one required skill is required.")
    
    return errors


# Event creation (POST)
@app.route('/eventform', methods=['POST'])
def create_event():
    data = request.json
    errors = validate_event_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    event = {
        'eventName': data['eventName'],
        'location': data['location'],
        'requiredSkills': data.get('requiredSkills', []),
        'urgency': data['urgency'],
        'eventDate': data['eventDate']
    }
    
    events.append(event)
    
    # Find and notify matching volunteers
    matches = find_best_matches(event)
    for match in matches:
        notification_message = f"New event matching your skills: {event['eventName']} on {event['eventDate']}"
        create_notification(
            match['username'],
            notification_message,
            'event_match',
            event['eventName']
        )
    
    return jsonify({
        'message': 'Event created successfully',
        'event': event,
        'matches': matches
    }), 201


# Get all events (GET)
@app.route('/eventform', methods=['GET'])
def get_events():
    return jsonify({'events': events}), 200

CORS(app, resources={r"/volunteer/*": {"origins": "http://localhost:3000"}})

users = []

def validate_profile_data(data, update=False):
    errors = []

    if 'email' in data:
        if len(data['email']) > 50:
            errors.append('Email cannot exceed 50 characters.')
        if not isinstance(data['email'], str):
            errors.append('Email must be a string.')

    if 'skills' in data and not isinstance(data['skills'], list):
        errors.append('Skills must be a list.')

    if 'preferences' in data and not isinstance(data['preferences'], str):
        errors.append('Preferences must be a string.')

    return errors

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Volunteer Management App Backend!"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    errors = validate_profile_data(data)

    if not data.get('username'):
        errors.append('Username is required.')
    elif len(data['username']) < 3 or len(data['username']) > 30:
        errors.append('Username must be between 3 and 30 characters.')

    if not data.get('password'):
        errors.append('Password is required.')
    elif len(data['password']) < 6:
        errors.append('Password must be at least 6 characters long.')

    if not data.get('email'):
        errors.append('Email is required.')

    if errors:
        return jsonify({'errors': errors}), 400

    for user in users:
        if user['username'] == data['username']:
            return jsonify({'error': 'User already exists'}), 400

    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    user_info = {
        'username': data['username'],
        'password': hashed_password,
        'email': data['email'],
        'skills': data.get('skills', []),
        'preferences': data.get('preferences', '')
    }
    users.append(user_info)

    response_user_info = {
        'username': data['username'],
        'email': data['email'],
        'skills': data.get('skills', []),
        'preferences': data.get('preferences', '')
    }

    return jsonify({'message': 'User registered successfully', 'user': response_user_info}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json

    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    for user in users:
        if user['username'] == data['username']:
            if bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
                return jsonify({'message': 'Login successful'}), 200
            else:
                return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    for user in users:
        if user['username'] == username:
            response_user_info = {
                'username': user['username'],
                'email': user['email'],
                'skills': user['skills'],
                'preferences': user['preferences']
            }
            return jsonify({'user': response_user_info}), 200

    return jsonify({'error': 'User not found'}), 404

@app.route('/profile/<username>', methods=['PUT'])
def update_profile(username):
    data = request.json
    errors = validate_profile_data(data, update=True)

    if errors:
        return jsonify({'errors': errors}), 400

    for user in users:
        if user['username'] == username:
            user['email'] = data.get('email', user['email'])
            user['skills'] = data.get('skills', user['skills'])
            user['preferences'] = data.get('preferences', user['preferences'])

            response_user_info = {
                'username': user['username'],
                'email': user['email'],
                'skills': user['skills'],
                'preferences': user['preferences']
            }

            return jsonify({'message': 'Profile updated successfully', 'user': response_user_info}), 200

    return jsonify({'error': 'User not found'}), 404

'''
Matching Module
'''

matches = []
def calculate_match_score(volunteer_skills, event_required_skills):
    """Calculate match score between volunteer and event."""
    if not volunteer_skills or not event_required_skills:
        return 0
    
    matching_skills = set(volunteer_skills) & set(event_required_skills)
    total_required_skills = len(event_required_skills)
    
    if total_required_skills == 0:
        return 0
        
    return len(matching_skills) / total_required_skills * 100

def find_best_matches(event, max_matches=5):
    """Find the best volunteer matches for an event."""
    event_scores = []
    
    for user in users:
        if 'skills' not in user:
            continue
            
        score = calculate_match_score(user['skills'], event['requiredSkills'])
        if score > 50:  # Only consider matches above 50% compatibility
            event_scores.append({
                'username': user['username'],
                'score': score,
                'email': user['email']
            })
    
    # Sort by score in descending order and return top matches
    return sorted(event_scores, key=lambda x: x['score'], reverse=True)[:max_matches]

@app.route('/matches/event/<event_name>', methods=['GET'])
def get_event_matches(event_name):
    """Get matches for a specific event."""
    event = next((e for e in events if e['eventName'] == event_name), None)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
        
    matches = find_best_matches(event)
    return jsonify({'matches': matches}), 200

@app.route('/matches/volunteer/<username>', methods=['GET'])
def get_volunteer_matches(username):
    """Get matching events for a volunteer."""
    user = next((u for u in users if u['username'] == username), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    matching_events = []
    for event in events:
        score = calculate_match_score(user.get('skills', []), event['requiredSkills'])
        if score > 50:
            matching_events.append({
                'event': event,
                'matchScore': score
            })
            
    return jsonify({'matches': matching_events}), 200

'''
Notification Module
'''

def create_notification(username, message, notification_type, related_id=None):
    """Create a new notification for a user."""
    if username not in notifications:
        notifications[username] = []
        
    notification = {
        'id': len(notifications[username]) + 1,
        'message': message,
        'type': notification_type,
        'timestamp': datetime.now().isoformat(),
        'read': False,
        'related_id': related_id
    }
    
    notifications[username].append(notification)
    return notification

@app.route('/notifications/<username>', methods=['GET'])
def get_notifications(username):
    """Get all notifications for a user."""
    user_notifications = notifications.get(username, [])
    return jsonify({'notifications': user_notifications}), 200

@app.route('/notifications/<username>/mark-read', methods=['POST'])
def mark_notifications_read(username):
    """Mark notifications as read."""
    notification_ids = request.json.get('notification_ids', [])
    if username not in notifications:
        return jsonify({'error': 'No notifications found'}), 404
        
    for notification in notifications[username]:
        if notification['id'] in notification_ids:
            notification['read'] = True
            
    return jsonify({'message': 'Notifications marked as read'}), 200

# Notification checker background task
def check_upcoming_events():
    """Background task to check for upcoming events and send reminders."""
    while True:
        current_time = datetime.now()
        for event in events:
            event_date = datetime.strptime(event['eventDate'], '%Y-%m-%d')
            
            # Send reminder 24 hours before event
            if current_time + timedelta(days=1) >= event_date:
                matches = find_best_matches(event)
                for match in matches:
                    create_notification(
                        match['username'],
                        f"Reminder: {event['eventName']} is tomorrow!",
                        'event_reminder',
                        event['eventName']
                    )
        
        time.sleep(3600)  # Check every hour

##################################################
users = [
    # Example user with a history
    {
        'username': 'john_doe',
        'email': 'john@example.com',
        'history': [
            {
                'eventName': 'Houston Marathon',
                'description': 'Gave water to runners',
                'location': 'Houston, TX',
                'requiredSkills': 'Water handing skills max lvl',
                'urgency': 'Urgent',
                'date': 'January 2023',
                'participationStatus': 'Not Participating'
            }
        ]
    }
]
def find_user(username):
    for user in users:
        if user['username'] == username:
            return user
    return None

# Route to get volunteer history for a specific user
@app.route('/volunteer/<username>/history', methods=['GET'])
def get_volunteer_history(username):
    for user in users:
        if user['username'] == username:
            return jsonify({'username': user['username'], 'history': user['history']}), 200
    return jsonify({'error': 'User not found'}), 404

@app.route('/volunteer/<username>/history', methods=['POST'])
def add_volunteer_history(username):
    for user in users:
        if user['username'] == username:
            new_event = request.json
            user['history'].append(new_event)
            return jsonify({'username': user['username'], 'history': user['history']}), 201
    return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    reminder_thread = threading.Thread(target=check_upcoming_events, daemon=True)
    reminder_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)