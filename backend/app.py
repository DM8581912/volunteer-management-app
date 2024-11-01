from flask import Flask, request, jsonify
import bcrypt
from flask_cors import CORS
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from supabase import create_client

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
