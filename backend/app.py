import logging
from typing import Optional

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=[os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000')])

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Constants
MATCH_THRESHOLD = 50
MAX_MATCHES = 5

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


# --- Validation ---

def validate_data(data: dict, schema: dict) -> list[str]:
    """Validate input data against a schema. Returns a list of error messages."""
    errors = []
    for field, rules in schema.items():
        is_required = rules.get('required', False)

        if is_required and field not in data:
            errors.append(f'{field} is required.')
            continue

        if field not in data:
            continue

        value = data[field]

        if 'type' in rules and not isinstance(value, rules['type']):
            errors.append(f'{field} must be of type {rules["type"].__name__}.')
        if 'min_length' in rules and len(value) < rules['min_length']:
            errors.append(f'{field} must be at least {rules["min_length"]} characters.')
        if 'max_length' in rules and len(value) > rules['max_length']:
            errors.append(f'{field} must not exceed {rules["max_length"]} characters.')
        if 'values' in rules and value not in rules['values']:
            errors.append(f'{field} must be one of: {", ".join(rules["values"])}')

    return errors


# --- Database Helpers ---

def get_user(username: str) -> Optional[dict]:
    """Fetch a user by username from Supabase."""
    response = supabase.table('users').select('*').eq('username', username).execute()
    return response.data[0] if response.data else None


def get_all_users() -> list[dict]:
    """Fetch all users from Supabase."""
    response = supabase.table('users').select('*').execute()
    return response.data or []


def get_all_events() -> list[dict]:
    """Fetch all events from Supabase."""
    response = supabase.table('events').select('*').execute()
    return response.data or []


def get_event_by_name(event_name: str) -> Optional[dict]:
    """Fetch an event by name from Supabase."""
    response = supabase.table('events').select('*').eq('eventName', event_name).execute()
    return response.data[0] if response.data else None


# --- Response Helper ---

def create_response(data: Optional[dict] = None, message: Optional[str] = None,
                    error=None, status: int = 200):
    """Build a consistent JSON response."""
    response = {}
    if data is not None:
        response.update(data)
    if message is not None:
        response['message'] = message
    if error is not None:
        response['error'] = error
    return jsonify(response), status


# --- Matching Logic ---

def calculate_match_score(volunteer_skills: list[str],
                          event_required_skills: list[str]) -> float:
    """Calculate match score (0-100) between volunteer skills and event requirements."""
    if not volunteer_skills or not event_required_skills:
        return 0.0

    normalized_volunteer = {skill.lower() for skill in volunteer_skills}
    normalized_required = {skill.lower() for skill in event_required_skills}

    matching_skills = normalized_volunteer & normalized_required
    total_required = len(normalized_required)

    return (len(matching_skills) / total_required) * 100 if total_required > 0 else 0.0


def find_best_matches(event: dict, max_matches: int = MAX_MATCHES) -> list[dict]:
    """Find the best volunteer matches for an event using Supabase data."""
    users = get_all_users()
    scored_matches = []

    logger.info("Finding matches for event: %s", event.get('eventName', 'unknown'))

    for user in users:
        user_skills = user.get('skills')
        if not user_skills:
            continue

        score = calculate_match_score(user_skills, event['requiredSkills'])
        logger.debug("User %s scored %.1f for event %s",
                      user['username'], score, event['eventName'])

        if score > MATCH_THRESHOLD:
            scored_matches.append({
                'username': user['username'],
                'score': score,
                'email': user.get('email', '')
            })

    return sorted(scored_matches, key=lambda x: x['score'], reverse=True)[:max_matches]


# --- Notification Helpers ---

def create_notification(username: str, message: str,
                        notification_type: str, related_id: Optional[str] = None) -> dict:
    """Create a new notification for a user in Supabase."""
    notification = {
        'username': username,
        'message': message,
        'type': notification_type,
        'read': False,
        'relatedId': related_id,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    supabase.table('notifications').insert(notification).execute()
    return notification


def get_user_notifications(username: str) -> list[dict]:
    """Fetch all notifications for a user from Supabase."""
    response = supabase.table('notifications').select('*').eq('username', username).execute()
    return response.data or []


def mark_notifications_as_read(username: str, notification_ids: list) -> bool:
    """Mark specific notifications as read in Supabase."""
    for notification_id in notification_ids:
        supabase.table('notifications') \
            .update({'read': True}) \
            .eq('username', username) \
            .eq('id', notification_id) \
            .execute()
    return True


# --- Routes ---

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

        hashed_password = bcrypt.hashpw(
            data['password'].encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

        user_info = {
            'username': data['username'],
            'password': hashed_password,
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
        logger.exception("Registration failed for user: %s", data.get('username', 'unknown'))
        return create_response(error='Registration failed. Please try again.', status=500)


@app.route('/login', methods=['POST'])
def login():
    """Authenticate a user."""
    try:
        data = request.json
        if not data.get('username') or not data.get('password'):
            return create_response(error='Username and password are required', status=400)

        user = get_user(data['username'])
        if user and bcrypt.checkpw(
            data['password'].encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            return create_response(message='Login successful')

        return create_response(error='Invalid credentials', status=401)
    except Exception as e:
        logger.exception("Login failed")
        return create_response(error='Login failed. Please try again.', status=500)


@app.route('/eventform', methods=['GET', 'POST'])
def handle_event():
    """List all events (GET) or create a new event (POST)."""
    if request.method == 'GET':
        try:
            events = get_all_events()
            return create_response(data={'events': events})
        except Exception as e:
            logger.exception("Failed to fetch events")
            return create_response(error='Failed to fetch events.', status=500)

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
        logger.exception("Failed to create event")
        return create_response(error='Failed to create event.', status=500)


@app.route('/matches/event/<event_name>', methods=['GET'])
def get_event_matches(event_name: str):
    """Get volunteer matches for a specific event."""
    try:
        event = get_event_by_name(event_name)
        if not event:
            return create_response(error='Event not found', status=404)

        matches = find_best_matches(event)
        return create_response(data={'matches': matches})
    except Exception as e:
        logger.exception("Failed to find matches for event: %s", event_name)
        return create_response(error='Failed to find matches.', status=500)


@app.route('/matches/volunteer/<username>', methods=['GET'])
def get_volunteer_matches(username: str):
    """Get matching events for a volunteer."""
    try:
        user = get_user(username)
        if not user:
            return create_response(error='User not found', status=404)

        events = get_all_events()
        matching_events = []

        for event in events:
            score = calculate_match_score(
                user.get('skills', []),
                event.get('requiredSkills', [])
            )
            if score > MATCH_THRESHOLD:
                matching_events.append({
                    'event': event,
                    'matchScore': score
                })

        return create_response(data={'matches': matching_events})
    except Exception as e:
        logger.exception("Failed to find matches for volunteer: %s", username)
        return create_response(error='Failed to find matches.', status=500)


@app.route('/notifications/<username>', methods=['GET'])
def get_notifications(username: str):
    """Get all notifications for a user."""
    try:
        notifications = get_user_notifications(username)
        return create_response(data={'notifications': notifications})
    except Exception as e:
        logger.exception("Failed to fetch notifications for: %s", username)
        return create_response(error='Failed to fetch notifications.', status=500)


@app.route('/notifications/<username>/mark-read', methods=['POST'])
def mark_notifications_read(username: str):
    """Mark specific notifications as read."""
    try:
        notification_ids = request.json.get('notification_ids', [])
        if not notification_ids:
            return create_response(error='No notification IDs provided', status=400)

        mark_notifications_as_read(username, notification_ids)
        return create_response(message='Notifications marked as read')
    except Exception as e:
        logger.exception("Failed to mark notifications for: %s", username)
        return create_response(error='Failed to update notifications.', status=500)


@app.route('/volunteer/<username>/history', methods=['GET'])
def get_volunteer_history(username: str):
    """Get a volunteer's participation history."""
    try:
        response = supabase.table('volunteerhistory').select('*').eq('username', username).execute()
        if not response.data:
            return create_response(error='User not found', status=404)
        return create_response(data={'username': username, 'history': response.data})
    except Exception as e:
        logger.exception("Failed to fetch history for: %s", username)
        return create_response(error='Failed to fetch volunteer history.', status=500)


@app.route('/volunteer/<username>/history', methods=['POST'])
def add_volunteer_event(username: str):
    """Add an event to a volunteer's history."""
    try:
        data = request.json
        user = get_user(username)
        if not user:
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
        return create_response(
            data={'username': username, 'history': event},
            status=201
        )
    except Exception as e:
        logger.exception("Failed to add history for: %s", username)
        return create_response(error='Failed to add volunteer event.', status=500)


app.register_blueprint(reporting, url_prefix="/admin")


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
