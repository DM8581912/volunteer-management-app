from flask import Flask, request, jsonify
import bcrypt
from flask_cors import CORS
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
CORS(app)

# Consolidated in-memory storage
db = {
    'users': [],
    'events': [],
    'notifications': {},
    'matches': []
}

# Sample data for testing
db['users'] = [
    {
        'username': 'johndoe',
        'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()),  # Hashed password
        'email': 'johndoe@example.com',
        'skills': ['python', 'flask', 'api'],
        'preferences': 'remote',
        'history': []
    },
    {
        'username': 'janedoe',
        'password': bcrypt.hashpw('mypassword'.encode('utf-8'), bcrypt.gensalt()),
        'email': 'janedoe@example.com',
        'skills': ['java', 'spring'],
        'preferences': 'in-person',
        'history': []
    }
]

db['events'] = [
    {
        'eventName': 'Code Sprint',
        'location': 'New York',
        'requiredSkills': ['python', 'flask'],
        'urgency': 'high',
        'eventDate': '2024-11-01'
    }
]

db['notifications'] = {
    'johndoe': [
        {
            'id': 1,
            'message': 'You have a new event match: Code Sprint',
            'type': 'event_match',
            'timestamp': datetime.now().isoformat(),
            'read': False,
            'related_id': 'Code Sprint'
        }
    ]
}

class ValidationError(Exception):
    pass

# Validation schemas
USER_SCHEMA = {
    'username': {'required': True, 'type': str, 'min_length': 3, 'max_length': 30},
    'password': {'required': True, 'type': str, 'min_length': 6},
    'email': {'required': True, 'type': str, 'max_length': 50},
    'skills': {'type': list},
    'preferences': {'type': str}
}

EVENT_SCHEMA = {
    'eventName': {'required': True, 'type': str, 'min_length': 5},
    'location': {'required': True, 'type': str},
    'requiredSkills': {'required': True, 'type': list, 'min_length': 1},
    'urgency': {'required': True, 'type': str, 'values': ['low', 'medium', 'high']},
    'eventDate': {'required': True, 'type': str}
}

# Helper Functions
def validate_data(data, schema):
    """Generic validation function for all data types"""
    errors = []
    
    for field, rules in schema.items():
        if 'required' in rules and rules['required'] and field not in data:
            errors.append(f'{field} is required.')
            continue
            
        if field not in data:
            continue
            
        value = data[field]
        
        if 'type' in rules and not isinstance(value, rules['type']):
            errors.append(f'{field} must be of type {rules["type"]}.')
        
        if 'min_length' in rules and len(value) < rules['min_length']:
            errors.append(f'{field} must be at least {rules["min_length"]} characters.')
            
        if 'max_length' in rules and len(value) > rules['max_length']:
            errors.append(f'{field} must not exceed {rules["max_length"]} characters.')
            
        if 'values' in rules and value not in rules['values']:
            errors.append(f'{field} must be one of: {", ".join(rules["values"])}')
            
    return errors

def get_user(username):
    """Centralized user lookup"""
    return next((user for user in db['users'] if user['username'] == username), None)

def get_event(event_name):
    """Centralized event lookup"""
    return next((event for event in db['events'] if event['eventName'] == event_name), None)

def create_response(data=None, message=None, error=None, status=200):
    """Standardized response creation"""
    response = {}
    if data is not None:
        response.update(data)
    if message is not None:
        response['message'] = message
    if error is not None:
        response['error'] = error
    return jsonify(response), status

# Matching System Functions
def calculate_match_score(volunteer_skills, event_required_skills):
    """Calculate match score between volunteer and event."""
    if not volunteer_skills or not event_required_skills:
        return 0
    
    volunteer_skills = {skill.lower() for skill in volunteer_skills}
    event_required_skills = {skill.lower() for skill in event_required_skills}

    matching_skills = set(volunteer_skills) & set(event_required_skills)
    total_required_skills = len(event_required_skills)
    
    if total_required_skills == 0:
        return 0
        
    return len(matching_skills) / total_required_skills * 100

def find_best_matches(event, max_matches=5):
    """Find the best volunteer matches for an event."""
    event_scores = []
    
    for user in db['users']:
        if 'skills' not in user:
            continue
            
        score = calculate_match_score(user['skills'], event['requiredSkills'])
        if score > 50:  # Only consider matches above 50% compatibility
            event_scores.append({
                'username': user['username'],
                'score': score,
                'email': user['email']
            })
    
    return sorted(event_scores, key=lambda x: x['score'], reverse=True)[:max_matches]

# Notification System Functions
def create_notification(username, message, notification_type, related_id=None):
    """Create a new notification for a user."""
    if username not in db['notifications']:
        db['notifications'][username] = []
        
    notification = {
        'id': len(db['notifications'][username]) + 1,
        'message': message,
        'type': notification_type,
        'timestamp': datetime.now().isoformat(),
        'read': False,
        'related_id': related_id
    }
    
    db['notifications'][username].append(notification)
    return notification

def check_upcoming_events():
    """Background task to check for upcoming events and send reminders."""
    while True:
        current_time = datetime.now()
        for event in db['events']:
            try:
                event_date = datetime.strptime(event['eventDate'], '%Y-%m-%d')
                
                # Send reminder 24 hours before event
                if current_time + timedelta(days=1) >= event_date >= current_time:
                    matches = find_best_matches(event)
                    for match in matches:
                        create_notification(
                            match['username'],
                            f"Reminder: {event['eventName']} is tomorrow!",
                            'event_reminder',
                            event['eventName']
                        )
            except ValueError:
                continue  # Skip events with invalid dates
                
        time.sleep(1)  # Check every hour

# Routes
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        errors = validate_data(data, USER_SCHEMA)
        if errors:
            return create_response(error=errors, status=400)

        if get_user(data['username']):
            return create_response(error='User already exists', status=400)

        user_info = {
            'username': data['username'],
            'password': bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()),
            'email': data['email'],
            'skills': data.get('skills', []),
            'preferences': data.get('preferences', ''),
            'history': []
        }
        db['users'].append(user_info)

        response_data = {k: v for k, v in user_info.items() if k != 'password'}
        return create_response(
            data={'user': response_data},
            message='User registered successfully',
            status=201
        )
    except Exception as e:
        return create_response(error=str(e), status=500)

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data.get('username') or not data.get('password'):
            return create_response(error='Username and password are required', status=400)

        user = get_user(data['username'])
        if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
            return create_response(message='Login successful')
        return create_response(error='Invalid credentials', status=401)
    except Exception as e:
        return create_response(error=str(e), status=500)

@app.route('/profile/<username>', methods=['GET', 'PUT'])
def handle_profile(username):
    try:
        user = get_user(username)
        if not user:
            return create_response(error='User not found', status=404)

        if request.method == 'GET':
            response_data = {k: v for k, v in user.items() if k != 'password'}
            return create_response(data={'user': response_data})

        data = request.json
        errors = validate_data(data, {k: v for k, v in USER_SCHEMA.items() if k != 'password'})
        if errors:
            return create_response(error=errors, status=400)

        for field in ['email', 'skills', 'preferences']:
            if field in data:
                user[field] = data[field]

        response_data = {k: v for k, v in user.items() if k != 'password'}
        return create_response(
            data={'user': response_data},
            message='Profile updated successfully'
        )
    except Exception as e:
        return create_response(error=str(e), status=500)

@app.route('/eventform', methods=['GET', 'POST'])
def handle_events():
    try:
        if request.method == 'GET':
            return create_response(data={'events': db['events']})

        data = request.json
        errors = validate_data(data, EVENT_SCHEMA)
        if errors:
            return create_response(error=errors, status=400)

        event = {
            'eventName': data['eventName'],
            'location': data['location'],
            'requiredSkills': data['requiredSkills'],
            'urgency': data['urgency'],
            'eventDate': data['eventDate']
        }
        db['events'].append(event)

        # Find and notify matching volunteers
        matches = find_best_matches(event)
        for match in matches:
            create_notification(
                match['username'],
                f"New event matching your skills: {event['eventName']} on {event['eventDate']}",
                'event_match',
                event['eventName']
            )

        return create_response(
            data={'event': event, 'matches': matches},
            message='Event created successfully',
            status=201
        )
    except Exception as e:
        return create_response(error=str(e), status=500)

@app.route('/matches/event/<event_name>', methods=['GET'])
def get_event_matches(event_name):
    """Get matches for a specific event."""
    try:
        event = get_event(event_name)
        if not event:
            return create_response(error='Event not found', status=404)
            
        matches = find_best_matches(event)
        return create_response(data={'matches': matches})
    except Exception as e:
        return create_response(error=str(e), status=500)

@app.route('/matches/volunteer/<username>', methods=['GET'])
def get_volunteer_matches(username):
    """Get matching events for a volunteer."""
    try:
        user = get_user(username)
        if not user:
            return create_response(error='User not found', status=404)
            
        matching_events = []
        for event in db['events']:
            score = calculate_match_score(user.get('skills', []), event['requiredSkills'])
            if score > 50:
                matching_events.append({
                    'event': event,
                    'matchScore': score
                })
                
        return create_response(data={'matches': matching_events})
    except Exception as e:
        return create_response(error=str(e), status=500)

@app.route('/notifications/<username>', methods=['GET'])
def get_notifications(username):
    """Get all notifications for a user."""
    try:
        user_notifications = db['notifications'].get(username, [])
        return create_response(data={'notifications': user_notifications})
    except Exception as e:
        return create_response(error=str(e), status=500)

@app.route('/notifications/<username>/mark-read', methods=['POST'])
def mark_notifications_read(username):
    """Mark notifications as read."""
    try:
        notification_ids = request.json.get('notification_ids', [])
        if username not in db['notifications']:
            return create_response(error='No notifications found', status=404)
            
        for notification in db['notifications'][username]:
            if notification['id'] in notification_ids:
                notification['read'] = True
                
        return create_response(message='Notifications marked as read')
    except Exception as e:
        return create_response(error=str(e), status=500)

@app.route('/volunteer/<username>/history', methods=['GET', 'POST'])
def handle_volunteer_history(username):
    """Handle volunteer history operations."""
    try:
        user = get_user(username)
        if not user:
            return create_response(error='User not found', status=404)

        if request.method == 'GET':
            return create_response(data={
                'username': user['username'],
                'history': user.get('history', [])
            })

        # POST method
        new_event = request.json
        if 'history' not in user:
            user['history'] = []
        user['history'].append(new_event)
        
        return create_response(
            data={'username': user['username'], 'history': user['history']},
            message='History updated successfully',
            status=201
        )
    except Exception as e:
        return create_response(error=str(e), status=500)

# Start the server
if __name__ == '__main__':
    reminder_thread = threading.Thread(target=check_upcoming_events, daemon=True)
    reminder_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
