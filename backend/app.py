import logging
from flask import Flask, request, jsonify
import bcrypt
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
from supabase import create_client
from reporting import reporting

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    'password': {'required': True, 'type': str, 'min_length': 8},
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
    """Validate input data against a schema definition."""
    errors = []
    for field, rules in schema.items():
        if rules.get('required') and field not in data:
            errors.append(f'{field} is required.')
            continue
        if field not in data:
            continue
        value = data[field]
        if 'type' in rules and not isinstance(value, rules['type']):
            errors.append(f'{field} must be of type {rules["type"].__name__}.')
        if 'min_length' in rules:
            if isinstance(value, (str, list)) and len(value) < rules['min_length']:
                errors.append(f'{field} must be at least {rules["min_length"]} characters.')
        if 'max_length' in rules:
            if isinstance(value, str) and len(value) > rules['max_length']:
                errors.append(f'{field} must not exceed {rules["max_length"]} characters.')
        if 'values' in rules and value not in rules['values']:
            errors.append(f'{field} must be one of: {", ".join(rules["values"])}')
    return errors


def get_user(username):
    """Fetch a user from the database by username."""
    response = supabase.table('users').select('*').eq('username', username).execute()
    return response.data[0] if response.data else None


def create_response(data=None, message=None, error=None, status=200):
    """Build a standardized JSON response."""
    response = {}
    if data is not None:
        response.update(data)
    if message is not None:
        response['message'] = message
    if error is not None:
        response['error'] = error
    return jsonify(response), status


def calculate_match_score(volunteer_skills, event_required_skills):
    """Calculate match score between volunteer skills and event requirements.

    Returns a percentage (0-100) of required skills matched.
    """
    if not volunteer_skills or not event_required_skills:
        return 0

    volunteer_skills_lower = {skill.lower() for skill in volunteer_skills}
    event_skills_lower = {skill.lower() for skill in event_required_skills}

    matching_skills = volunteer_skills_lower & event_skills_lower
    total_required = len(event_skills_lower)

    return (len(matching_skills) / total_required) * 100 if total_required > 0 else 0


def find_best_matches(event, max_matches=5):
    """Find the best volunteer matches for an event using the database."""
    event_scores = []

    users_response = supabase.table('users').select('username, email, skills').execute()
    users = users_response.data if users_response.data else []

    for user in users:
        user_skills = user.get('skills', [])
        if not user_skills:
            continue

        score = calculate_match_score(user_skills, event.get('requiredSkills', []))
        logger.debug("User %s scored %.1f for event %s", user['username'], score, event.get('eventName'))

        if score > 50:
            event_scores.append({
                'username': user['username'],
                'score': score,
                'email': user.get('email', '')
            })

    return sorted(event_scores, key=lambda x: x['score'], reverse=True)[:max_matches]


def create_notification(username, message, notification_type, related_id=None):
    """Create a new notification for a user in the database."""
    notification = {
        'username': username,
        'message': message,
        'type': notification_type,
        'relatedId': related_id,
        'read': False,
        'createdAt': datetime.now(timezone.utc).isoformat()
    }

    try:
        supabase.table('notifications').insert(notification).execute()
        logger.info("Notification created for user %s: %s", username, notification_type)
    except Exception as e:
        logger.error("Failed to create notification for %s: %s", username, e)

    return notification


def check_upcoming_events():
    """Check for upcoming events and send reminder notifications to matched volunteers."""
    current_time = datetime.now()

    try:
        events_response = supabase.table('events').select('*').execute()
        events = events_response.data if events_response.data else []
    except Exception as e:
        logger.error("Failed to fetch events for reminders: %s", e)
        return

    for event in events:
        try:
            event_date = datetime.strptime(event['eventDate'], '%Y-%m-%d')
            if current_time + timedelta(days=1) >= event_date >= current_time:
                matches = find_best_matches(event)
                for match in matches:
                    create_notification(
                        match['username'],
                        f"Reminder: {event['eventName']} is tomorrow!",
                        'event_reminder',
                        event.get('eventName')
                    )
        except (ValueError, KeyError):
            continue


# Routes

@app.route('/register', methods=['POST'])
def register():
    """Register a new user."""
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
        logger.error("Registration failed: %s", e)
        return create_response(error=str(e), status=500)


@app.route('/login', methods=['POST'])
def login():
    """Authenticate a user."""
    try:
        data = request.json
        if not data.get('username') or not data.get('password'):
            return create_response(error='Username and password are required', status=400)

        user = get_user(data['username'])
        if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
            return create_response(message='Login successful')
        return create_response(error='Invalid credentials', status=401)
    except Exception as e:
        logger.error("Login failed: %s", e)
        return create_response(error=str(e), status=500)


@app.route('/eventform', methods=['GET', 'POST'])
def handle_event():
    """List events or create a new event."""
    if request.method == 'GET':
        try:
            events = supabase.table('events').select('*').execute().data
            return create_response(data={'events': events})
        except Exception as e:
            logger.error("Failed to fetch events: %s", e)
            return create_response(error=str(e), status=500)

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
        logger.error("Event creation failed: %s", e)
        return create_response(error=str(e), status=500)


@app.route('/matches/event/<event_name>', methods=['GET'])
def get_event_matches(event_name):
    """Get volunteer matches for a specific event."""
    try:
        event_response = supabase.table('events').select("*").eq('eventName', event_name).execute()
        event = event_response.data[0] if event_response.data else None
        if not event:
            return create_response(error='Event not found', status=404)

        matches = find_best_matches(event)
        return create_response(data={'matches': matches})
    except Exception as e:
        logger.error("Failed to get matches for event %s: %s", event_name, e)
        return create_response(error=str(e), status=500)


@app.route('/matches/volunteer/<username>', methods=['GET'])
def get_volunteer_matches(username):
    """Get matching events for a volunteer based on their skills."""
    try:
        user_response = supabase.table('users').select("*").eq('username', username).execute()
        user = user_response.data[0] if user_response.data else None
        if not user:
            return create_response(error='User not found', status=404)

        events_response = supabase.table('events').select("*").execute()
        events = events_response.data if events_response.data else []

        matching_events = []
        for event in events:
            score = calculate_match_score(user.get('skills', []), event.get('requiredSkills', []))
            if score > 50:
                matching_events.append({
                    'event': event,
                    'matchScore': score
                })

        return create_response(data={'matches': matching_events})
    except Exception as e:
        logger.error("Failed to get matches for volunteer %s: %s", username, e)
        return create_response(error=str(e), status=500)


@app.route('/notifications/<username>', methods=['GET'])
def get_notifications(username):
    """Get all notifications for a user."""
    try:
        response = supabase.table('notifications').select('*').eq('username', username).execute()
        notifications = response.data if response.data else []
        return create_response(data={'notifications': notifications})
    except Exception as e:
        logger.error("Failed to get notifications for %s: %s", username, e)
        return create_response(error=str(e), status=500)


@app.route('/notifications/<username>/mark-read', methods=['POST'])
def mark_notifications_read(username):
    """Mark specific notifications as read."""
    try:
        notification_ids = request.json.get('notification_ids', [])
        if not notification_ids:
            return create_response(error='No notification IDs provided', status=400)

        for nid in notification_ids:
            supabase.table('notifications').update({'read': True}).eq('id', nid).eq('username', username).execute()

        return create_response(message='Notifications marked as read')
    except Exception as e:
        logger.error("Failed to mark notifications read for %s: %s", username, e)
        return create_response(error=str(e), status=500)


@app.route('/volunteer/<username>/history', methods=['GET'])
def get_volunteer_history(username):
    """Get volunteer history for a user."""
    try:
        response = supabase.table('volunteerhistory').select("*").eq('username', username).execute()
        if not response.data:
            return create_response(error='User not found', status=404)
        return create_response(data={'username': username, 'history': response.data})
    except Exception as e:
        logger.error("Failed to get volunteer history for %s: %s", username, e)
        return create_response(error=str(e), status=500)


@app.route('/volunteer/<username>/history', methods=['POST'])
def add_volunteer_event(username):
    """Add a volunteer history entry for a user."""
    try:
        data = request.json
        user_response = supabase.table('users').select("*").eq('username', username).execute()
        if not user_response.data:
            return create_response(error='User not found', status=404)

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
        return create_response(data={'username': username, 'history': event}, status=201)
    except Exception as e:
        logger.error("Failed to add volunteer event for %s: %s", username, e)
        return create_response(error=str(e), status=500)


app.register_blueprint(reporting, url_prefix="/admin")


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
