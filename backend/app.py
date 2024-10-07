from flask import Flask, request, jsonify
import bcrypt

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
