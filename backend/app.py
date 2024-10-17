from flask import Flask, request, jsonify
import bcrypt
from flask_cors import CORS

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
    print("Received data:", data)  # Add this to confirm Flask is receiving the request

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
    return jsonify({'message': 'Event created successfully', 'event': event}), 201

# Get all events (GET)
@app.route('/eventform', methods=['GET'])
def get_events():
    return jsonify({'events': events}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
