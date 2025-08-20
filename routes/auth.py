from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
import re
from dotenv import load_dotenv


load_dotenv()

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=20000)
    client.admin.command('ping')
    print("MongoDB connected successfully!")
except Exception as e:
    print(f" MongoDB connection failed: {e}")
    print("Please set MONGO_URI to your Atlas URI or start local MongoDB on 27017")
    raise

db = client["RUSwapping"]
users_collection = db['users']

auth = Blueprint('auth', __name__)

def is_rutgers_email(email):
    """Check if email is a valid Rutgers email address"""
    # Only allow @scarletmail.rutgers.edu addresses
    return email.endswith('@scarletmail.rutgers.edu')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not all([email, password, name]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if not is_rutgers_email(email):
            return jsonify({'error': 'Please use a valid Rutgers email address'}), 400
        
        try:
            if users_collection.find_one({'email': email}):
                return jsonify({'error': 'Email already registered'}), 400
            
            user_data = {
                'email': email,
                'password_hash': generate_password_hash(password),
                'name': name,
                'created_at': datetime.utcnow()
            }
            
            result = users_collection.insert_one(user_data)
            
            return jsonify({'message': 'Registration successful! Please log in.'}), 201
            
        except Exception as e:
            print(f"Database error during registration: {e}")
            return jsonify({'error': 'Registration failed. Please try again.'}), 500
    
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        try:
            # Check if email and password are valid
            user_data = users_collection.find_one({'email': email})
            if user_data and check_password_hash(user_data['password_hash'], password):
                # Store user info in session
                session['user_id'] = str(user_data['_id'])
                session['user_email'] = user_data['email']
                session['user_name'] = user_data['name']
                return jsonify({'message': 'Login successful!', 'redirect': url_for('dashboard')}), 200
            else:
                return jsonify({'error': 'Invalid email or password'}), 401
        except Exception as e:
            print(f"Database error during login: {e}")
            return jsonify({'error': 'Login failed. Please try again.'}), 500
    else:
        return render_template('login.html')

@auth.route('/logout')
def logout():
    # Clear session
    session.clear()
    return redirect(url_for('home'))

@auth.route('/get-user-info', methods=['GET'])
def get_user_info():
	"""Get current user's information for display."""

	current_user = get_current_user()
	
	if current_user:
		return jsonify({
			'id': current_user['id'],
			'email': current_user['email'],
			'name': current_user.get('name', 'User')
		})
	else:
		return jsonify({'error': 'User not found'}), 404

def login_required(f):
    """Decorator to require login for protected routes"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_current_user():
    """Get current user data from session"""
    if 'user_id' not in session:
        return None
    
    try:
        user_data = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        if user_data:
            return {
                'id': str(user_data['_id']),
                'email': user_data['email'],
                'name': user_data['name']
            }
    except Exception:
        pass
    
    return None 