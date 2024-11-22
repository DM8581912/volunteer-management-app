from flask import Flask, request, jsonify
import bcrypt
from flask_cors import CORS
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from supabase import create_client
from reporting import reporting


# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

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

def validate_data(data, schema):
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
    response = supabase.table('users').select('*').eq('username', username).execute()
    return response.data[0] if response.data else None

def create_response(data=None, message=None, error=None, status=200):
    response = {}
    if data is not None:
        response.update(data)
    if message is not None:
        response['message'] = message
    if error is not None:
        response['error'] = error
    return jsonify(response), status

def calculate_match_score(volunteer_skills, event_required_skills):
    """Calculate match score between volunteer and event."""
    if not volunteer_skills or not event_required_skills:
        return 0
    
    # Normalize skills to lowercase for case-insensitive comparison
    volunteer_skills = {skill.lower() for skill in volunteer_skills}
    event_required_skills = {skill.lower() for skill in event_required_skills}

    matching_skills = volunteer_skills & event_required_skills
    total_required_skills = len(event_required_skills)
    
    return (len(matching_skills) / total_required_skills) * 100 if total_required_skills > 0 else 0



def find_best_matches(event, max_matches=5):
    """Find the best volunteer matches for an event."""
    event_scores = []
    
    print("Finding matches for event:", event)  # Log event details
    
    for user in db['users']:
        if 'skills' not in user:
            continue
        
        # Log each user’s skills to debug matching
        print("Checking user:", user['username'], "with skills:", user['skills'])
        print("Event required skills:", event['requiredSkills'])
        
        score = calculate_match_score(user['skills'], event['requiredSkills'])
        print("Calculated match score:", score)  # Debug score calculation
        
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

def check_upcoming_events(test_mode=False):
    current_time = datetime.now()
    print("Checking events:", db['events'])  # Add this line for debugging
    for event in db['events']:
        try:
            event_date = datetime.strptime(event['eventDate'], '%Y-%m-%d')
            if current_time + timedelta(days=1) >= event_date >= current_time:
                # Find and notify matching volunteers
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
    if test_mode:
        return  # Ensure this returns when called in test mode


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
            'password': bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'email': data['email'],
            'skills': data.get('skills', []),
            'preferences': data.get('preferences', ''),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        supabase.table('users').insert(user_info).execute()

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
        if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
            return create_response(message='Login successful')
        return create_response(error='Invalid credentials', status=401)
    except Exception as e:
        return create_response(error=str(e), status=500)

@app.route('/eventform', methods=['GET', 'POST'])
def handle_event():
    if request.method == 'GET':
        events = supabase.table('events').select('*').execute().data
        return create_response(data={'events': events})

    elif request.method == 'POST':
        try:
            data = request.json
            errors = validate_data(data, EVENT_SCHEMA)
            if errors:
                return create_response(error=errors, status=400)

            event = {
                'eventName': data['eventName'],
                'location': data['location'],
                'requiredSkills': data['requiredSkills'],
                'urgency': data['urgency'],
                'eventDate': data['eventDate'],
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
            supabase.table('events').insert(event).execute()

            return create_response(
                data={'event': event},
                message='Event created successfully',
                status=201
            )
        except Exception as e:
            return create_response(error=str(e), status=500)

@app.route('/matches/event/<event_name>', methods=['GET'])
def get_event_matches(event_name):
    """Get matches for a specific event."""
    try:
        event_response = supabase.table('events').select("*").eq('eventName', event_name).execute()
        event = event_response.data[0] if event_response.data else None
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
        user_response = supabase.table('users').select("*").eq('username', username).execute()
        user = user_response.data[0] if user_response.data else None
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

# Example Route: Get Volunteer History
@app.route('/volunteer/<username>/history', methods=['GET'])
def get_volunteer_history(username):
    try:
        response = supabase.table('volunteerhistory').select("*").eq('username', username).execute()
        if not response.data:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'username': username, 'history': response.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Example Route: Add Volunteer Event
@app.route('/volunteer/<username>/history', methods=['POST'])
def add_volunteer_event(username):
    try:
        data = request.json
        # Ensure that user exists before adding history
        user_response = supabase.table('users').select("*").eq('username', username).execute()
        if not user_response.data:
            return jsonify({'error': 'User not found'}), 404
        
        event = {
            'username': username,
            'eventname': data.get('eventName'),
            'description': data.get('description'),
            'location': data.get('location'),
            'requiredskills': data.get('requiredSkills', []),
            'urgency': data.get('urgency'),
            'eventdate': data.get('eventDate'),
            'participationstatus': data.get('participationStatus')
        }
        supabase.table('volunteerhistory').insert(event).execute()
        return jsonify({'username': username, 'history': event}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

app.register_blueprint(reporting, url_prefix="/admin")


# Start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
