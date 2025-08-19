import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from auth import auth, login_required
from swap_requests import swap_requests_bp
import os
from auth import get_current_user
from bson import ObjectId
from datetime import datetime
from pymongo import MongoClient
from utils.utils import to_jsonable
import json


load_dotenv()

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=20000)
db = client["RUSwapping"]

users_collection = db['users']
swap_requests_collection = db['swap_requests'] 

# Flask application setup
app = Flask(__name__)

# Secret key used for session cookies (loaded from env with a dev fallback)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

# Register authentication routes (login, register, logout)
app.register_blueprint(auth)

# Register swap requests blueprint
app.register_blueprint(swap_requests_bp)

@app.route('/')
def home():
	"""Render the public home page."""
	return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
	"""Render the logged-in user's dashboard."""
	return render_template('dashboard.html')

# Additional endpoints for frontend functionality
@app.route('/get-matches', methods=['GET'])
@login_required
def get_matches():
	"""Get mutual matches for the current user."""
	current_user = get_current_user()
	if not current_user:
		return jsonify([])

	# Fetch current user's active swap request
	my_request = swap_requests_collection.find_one({
		'user_id': current_user['id'],
		'type': 'swap_request'
	})
	if not my_request:
		return jsonify([])

	my_current_apartment = my_request.get('current_apartment')
	my_prefs = (my_request.get('preferences') or {})
	my_choices = [
		my_prefs.get('first_choice'),
		my_prefs.get('second_choice'),
		my_prefs.get('third_choice')
	]

	matches = []

	# loop through all users except my user
	for other_user in users_collection.find():
		if other_user.get('_id') == current_user['id']:
			continue

		other_user_prefs = (other_user.get('preferences') or {})
		other_user_current_apartment = other_user.get('current_apartment')
	
		other_user_choices = [
			other_user_prefs.get('first_choice'),
			other_user_prefs.get('second_choice'),
			other_user_prefs.get('third_choice')
		]
		
		for choice in other_user_choices:
			if choice == my_current_apartment:
				other_user_wants_my_level = other_user_choices.index(choice) + 1
				break

		for choice in my_choices:
			if choice == other_user_current_apartment:
				my_user_wants_other_level = my_choices.index(choice) + 1
				break

		if other_user_wants_my_level and my_user_wants_other_level:
			matches.append({
				'other_user_id': other_user.get('_id'),
				'other_user_name': other_user.get('name'),
				'other_user_current_apartment': other_user_current_apartment,
				'my_user_wants_other_level': my_user_wants_other_level,
				'other_user_email_display': other_user.get('email', '')
			})

	return jsonify(matches)


@app.route('/get-user-info', methods=['GET'])
@login_required
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


def show_requests():
	"""Show all requests."""

	requests = swap_requests_collection.find({'type': 'swap_request'})
	for request in requests:
		print(request)

if __name__ == '__main__':
	show_requests()
	app.run(debug=True) 