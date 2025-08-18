from collections import UserList
import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from auth import auth, login_required
import os
from auth import get_current_user
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json


load_dotenv()

# Flask application setup
app = Flask(__name__)
# Secret key used for session cookies (loaded from env with a dev fallback)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

# Database connection
# MONGO_URI points to your MongoDB server/cluster
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
# Create a client and select the application database
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=20000)
db = client["RUSwapping"]

# Collections (tables) used by the app
users_collection = db['users']
swap_requests_collection = db['swap_requests']

# Helper function to convert MongoDB documents to JSON-serializable format
def to_jsonable(obj):
	if isinstance(obj, ObjectId):
		return str(obj)
	if isinstance(obj, list):
		return [to_jsonable(x) for x in obj]
	if isinstance(obj, dict):
		out = {}
		for k, v in obj.items():
			if k == '_id':
				out['id'] = str(v)
			else:
				out[k] = to_jsonable(v)
		return out
	return obj


# Register authentication routes (login, register, logout)
app.register_blueprint(auth)

@app.route('/')
def home():
	"""Render the public home page."""
	return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
	"""Render the logged-in user's dashboard."""
	return render_template('dashboard.html')

@app.route('/create-request', methods=['POST'])
@login_required
def create_request():
	"""Create a new swap request for the current user.

	Accepts JSON or form-encoded data with the following fields:
	- current_apartment (required)
	- current_room (optional)
	- first_choice, second_choice, third_choice (optional preferences)
	"""

	# Get the authenticated user from session
	current_user = get_current_user()

	# Read request payload 
	request_data = request.get_json(silent=True) 

	# Extract request fields
	current_apartment = request_data.get('current_apartment')
	current_room = request_data.get('current_room', '')
	first_choice = request_data.get('first_choice')
	second_choice = request_data.get('second_choice')
	third_choice = request_data.get('third_choice')

	# Makes sure that all the required fields are filled out
	if not current_apartment or not first_choice or not second_choice or not third_choice:
		return jsonify({'error': 'All fields are required'}), 400

	# Check if user already has a request
	existing_request = swap_requests_collection.find_one({
		'user_id': current_user['id'],
		'type': 'swap_request'
	})
	
	if existing_request:
		# User already has a request - return error
		return jsonify({'error': 'You already have a swap request. Please delete your existing request first or update it.'}), 400

	# Persist the swap request
	doc = {
		'user_id': current_user['id'],
		'user_name': current_user['name'],
		'current_apartment': current_apartment,
		'current_room': current_room,
		'preferences': {
			'first_choice': first_choice,
			'second_choice': second_choice,
			'third_choice': third_choice,
		},
		'created_at': datetime.utcnow(),
		'type': 'swap_request'
	}

	# Insert into MongoDB and return the new id
	res = swap_requests_collection.insert_one(doc)

	return jsonify({'message': 'Swap request created successfully!', 'request_id': str(res.inserted_id)}), 201

@app.route('/get-requests')
@login_required
def get_request():
	"""Return the current user's active swap request."""

	# Current user context
	current_user = get_current_user()
	
	# Find the user's request
	user_request = swap_requests_collection.find_one({
		'user_id': current_user['id'],
		'type': 'swap_request'
	})
	
	if user_request:
		# Mark as own request for frontend
		user_request['is_own'] = True
		return jsonify([to_jsonable(user_request)])
	else:
		return jsonify([])



#deletes request
@app.route('/delete-request', methods=['POST'])
@login_required
def delete_request():
	"""Delete a swap request for the current user."""
	# Read request payload
	request_data = request.get_json(silent=True)

	# Extract request id
	request_id = request_data.get('request_id')


		cur_a = req_a.get('current_apartment')
		prefs_a = req_a.get('preferences') or {}
		choices_a = [prefs_a.get('first_choice'), prefs_a.get('second_choice'), prefs_a.get('third_choice')]

		for j in range(i + 1, len(requests)):
			req_b = requests[j]
			user_b = str(req_b.get('user_id'))

			# Skip invalid or same-user comparisons
			if not user_a or not user_b or user_a == user_b:
				continue


			cur_b = req_b.get('current_apartment')
			prefs_b = req_b.get('preferences') or {}
			choices_b = [prefs_b.get('first_choice'), prefs_b.get('second_choice'), prefs_b.get('third_choice')]

			# Helper: return 1/2/3 rank if target is among choices; ignore None
			def rank(choices, target):
				if not target:
					return None
				for idx, val in enumerate(choices, start=1):
					if val and val == target:
						return idx
				return None

			a_wants_b = rank(choices_a, cur_b)
			b_wants_a = rank(choices_b, cur_a)

			# Mutual only if both sides rank the other
			if a_wants_b and b_wants_a:
				# Prevent duplicate pairs (A,B) and (B,A)
				pair = tuple(sorted([user_a, user_b]))
				if pair in seen_pairs:
					continue
				seen_pairs.add(pair)

				# Fetch minimal user info for display (name)
				user_a_doc = users_collection.find_one({'_id': ObjectId(user_a)}) if ObjectId.is_valid(user_a) else None
				user_b_doc = users_collection.find_one({'_id': ObjectId(user_b)}) if ObjectId.is_valid(user_b) else None

				matches.append({
					'user_a_id': user_a,
					'user_a_name': (user_a_doc or {}).get('name', 'Unknown User'),
					'user_a_current': cur_a,
					'user_a_rank': a_wants_b,
					'user_b_id': user_b,
					'user_b_name': (user_b_doc or {}).get('name', 'Unknown User'),
					'user_b_current': cur_b,
					'user_b_rank': b_wants_a
				})

	# Sort matches by best combined ranks for a consistent order
	matches.sort(key=lambda m: (min(m['user_a_rank'], m['user_b_rank']), m['user_a_rank'] + m['user_b_rank']))

	return matches


def show_requests():
	"""Show all requests."""

	requests = swap_requests_collection.find({'type': 'swap_request'})
	for request in requests:
		print(request)


if __name__ == '__main__':
	# Start the Flask development server
	show_requests()
	app.run(debug=True)	# Delete the request from MongoDB
	swap_requests_collection.delete_one({'_id': ObjectId(request_id)})

	return jsonify({'message': 'Swap request deleted successfully!'}), 200

#update request
@app.route('/update-request', methods=['POST'])
@login_required
def update_request():
	"""Update a swap request for the current user."""
	
	# Read request payload
	request_data = request.get_json(silent=True)

	# Extract request id
	request_id = request_data.get('request_id')
	
	# Update the request in MongoDB
	swap_requests_collection.update_one({'_id': ObjectId(request_id)}, {'$set': request_data})

	return jsonify({'message': 'Swap request updated successfully!'}), 200

# Additional endpoints for frontend functionality
@app.route('/get-matches', methods=['GET'])
@login_required
def get_mutual_matches():
	
	"""Get mutual matches for the current user."""
	current_user = get_current_user()
	
	# Get all swap requests
	all_requests = list(swap_requests_collection.find({'type': 'swap_request'}))
	
	# Get user's request
	user_request = next((req for req in all_requests if req['user_id'] == current_user['id']), None)
	if not user_request:
		return jsonify([])
	
	matches = []

	user_prefs = user_request.get('preferences', {})
	user_choices = [user_prefs.get('first_choice'), user_prefs.get('second_choice'), user_prefs.get('third_choice')]
	user_current = user_request.get('current_apartment')
	
	for other_request in all_requests:

		# Skip if the other request is the user's own request
		if other_request['user_id'] == current_user['id']:
			continue
			
		other_prefs = other_request.get('preferences', {})
		other_choices = [other_prefs.get('first_choice'), other_prefs.get('second_choice'), other_prefs.get('third_choice')]
		other_current = other_request.get('current_apartment')
		
	
		user_wants_other = None
		other_wants_user = None
		
		# Check if user wants other's current place
		for i, choice in enumerate(user_choices, 1):
			if choice == other_current:
				user_wants_other = i
				break
				
		# Check if other wants user's current place
		for i, choice in enumerate(other_choices, 1):
			if choice == user_current:
				other_wants_user = i
				break
		
		if user_wants_other and other_wants_user:
			# Check if there's mutual interest
			user_interest = swap_requests_collection.find_one({
				'user_id': current_user['id'],
				'other_user_id': other_request['user_id'],
				'type': 'interest'
			})
			
			other_interest = swap_requests_collection.find_one({
				'user_id': other_request['user_id'],
				'other_user_id': current_user['id'],
				'type': 'interest'
			})
			
			mutually_confirmed = user_interest and other_interest
			
			# Get other user's name
			other_user = users_collection.find_one({'_id': ObjectId(other_request['user_id'])})
			other_user_name = other_user.get('name', 'Unknown User') if other_user else 'Unknown User'
			
			matches.append({
				'other_user_id': str(other_request['user_id']),
				'other_user_name': other_user_name,
				'other_current_apartment': other_current,
				'other_current_room': other_request.get('current_room', ''),
				'my_preference_level': user_wants_other,
				'they_want_my_level': other_wants_user,
				'mutually_confirmed': mutually_confirmed,
				'i_expressed_interest': user_interest is not None,
				'they_expressed_interest': other_interest is not None,
				'other_user_email_display': other_user.get('email', '') if mutually_confirmed else 'Hidden until confirmed',
				'other_first_choice': other_prefs.get('first_choice'),
				'other_second_choice': other_prefs.get('second_choice'),
				'other_third_choice': other_prefs.get('third_choice')
			})
	
	return jsonify(matches)

@app.route('/express-interest', methods=['POST'])
@login_required
def express_interest():
	"""Express interest in another user's swap request."""
	current_user = get_current_user()
	request_data = request.get_json()
	other_user_id = request_data.get('other_user_id')
	
	if not other_user_id:
		return jsonify({'error': 'Other user ID is required'}), 400
	
	# Check if already expressed interest
	existing_interest = swap_requests_collection.find_one({
		'user_id': current_user['id'],
		'other_user_id': other_user_id,
		'type': 'interest'
	})
	
	if existing_interest:
		return jsonify({'error': 'Already expressed interest in this user'}), 400
	
	# Create interest record
	interest_doc = {
		'user_id': current_user['id'],
		'other_user_id': other_user_id,
		'type': 'interest',
		'created_at': datetime.utcnow()
	}
	
	swap_requests_collection.insert_one(interest_doc)
	
	return jsonify({'message': 'Interest expressed successfully!'}), 200

@app.route('/withdraw-interest', methods=['POST'])
@login_required
def withdraw_interest():
	"""Withdraw interest in another user's swap request."""
	current_user = get_current_user()
	request_data = request.get_json()
	other_user_id = request_data.get('other_user_id')
	
	if not other_user_id:
		return jsonify({'error': 'Other user ID is required'}), 400
	
	# Delete interest record
	result = swap_requests_collection.delete_one({
		'user_id': current_user['id'],
		'other_user_id': other_user_id,
		'type': 'interest'
	})
	
	if result.deleted_count > 0:
		return jsonify({'message': 'Interest withdrawn successfully!'}), 200
	else:
		return jsonify({'error': 'No interest found to withdraw'}), 404

@app.route('/remove-match', methods=['POST'])
@login_required
def remove_match():
	"""Remove a confirmed match."""
	current_user = get_current_user()
	request_data = request.get_json()
	other_user_id = request_data.get('other_user_id')
	
	if not other_user_id:
		return jsonify({'error': 'Other user ID is required'}), 400
	
	# Remove both interest records
	result = swap_requests_collection.delete_many({
		'$or': [
			{'user_id': current_user['id'], 'other_user_id': other_user_id},
			{'user_id': other_user_id, 'other_user_id': current_user['id']}
		],
		'type': 'interest'
	})
	
	if result.deleted_count > 0:
		return jsonify({'message': 'Match removed successfully!'}), 200
	else:
		return jsonify({'error': 'No match found to remove'}), 404

@app.route('/accept-interest', methods=['POST'])
@login_required
def accept_interest():
	"""Accept an incoming interest request from another user."""
	current_user = get_current_user()
	request_data = request.get_json()
	other_user_id = request_data.get('other_user_id')
	
	if not other_user_id:
		return jsonify({'error': 'Other user ID is required'}), 400
	
	# Check if there's an incoming interest request
	incoming_interest = swap_requests_collection.find_one({
		'user_id': other_user_id,
		'other_user_id': current_user['id'],
		'type': 'interest'
	})
	
	if not incoming_interest:
		return jsonify({'error': 'No incoming interest request found'}), 404
	
	# Check if user has already expressed interest back
	existing_interest = swap_requests_collection.find_one({
		'user_id': current_user['id'],
		'other_user_id': other_user_id,
		'type': 'interest'
	})
	
	if existing_interest:
		return jsonify({'error': 'You have already expressed interest in this user'}), 400
	
	# Create interest record to accept the request
	interest_doc = {
		'user_id': current_user['id'],
		'other_user_id': other_user_id,
		'type': 'interest',
		'created_at': datetime.utcnow()
	}
	
	swap_requests_collection.insert_one(interest_doc)
	
	return jsonify({'message': 'Interest accepted! You now have a confirmed match.'}), 200

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

@app.route('/create-requests/<request_id>', methods=['PUT'])
@login_required
def update_swap_request(request_id):
	"""Update an existing swap request."""
	current_user = get_current_user()
	
	# Verify the request belongs to the user
	existing_request = swap_requests_collection.find_one({
		'_id': ObjectId(request_id),
		'user_id': current_user['id'],
		'type': 'swap_request'
	})
	
	if not existing_request:
		return jsonify({'error': 'Request not found or not authorized'}), 404
	
	# Get update data
	request_data = request.get_json()
	
	# Validate required fields
	if not all([request_data.get('current_apartment'), request_data.get('first_choice'), 
				request_data.get('second_choice'), request_data.get('third_choice')]):
		return jsonify({'error': 'All fields are required'}), 400
	
	# Update the request
	update_data = {
		'current_apartment': request_data['current_apartment'],
		'current_room': request_data.get('current_room', ''),
		'preferences': {
			'first_choice': request_data['first_choice'],
			'second_choice': request_data['second_choice'],
			'third_choice': request_data['third_choice']
		},
		'updated_at': datetime.utcnow()
	}
	
	# Update the request in MongoDB
	result = swap_requests_collection.update_one(
		{'_id': ObjectId(request_id)},
		{'$set': update_data}
	)
	
	if result.modified_count > 0:
		return jsonify({'message': 'Swap request updated successfully!'}), 200
	else:
		return jsonify({'error': 'Failed to update request'}), 500

@app.route('/delete-requests/<request_id>', methods=['DELETE'])
@login_required
def delete_swap_request(request_id):
	"""Delete a swap request permanently."""
	current_user = get_current_user()
	
	# Permanently delete the request
	result = swap_requests_collection.delete_one(
		{'_id': ObjectId(request_id), 'user_id': current_user['id'], 'type': 'swap_request'}
	)

	# Delete associated interest records for this user
	swap_requests_collection.delete_many({
		'type': 'interest',
		'$or': [
			{'user_id': current_user['id']},
			{'other_user_id': current_user['id']}
		]
	})
	
	if result.deleted_count == 0:
		return jsonify({'error': 'Request not found or not authorized'}), 404
	
	return jsonify({'message': 'Request deleted successfully'}), 200


def match_users():
	"""Find mutual matches across swap requests based on exact preferences.

	Two different users match if:
	- A's current_apartment is in B's preferences, and
	- B's current_apartment is in A's preferences.

	Returns a list of dictionaries with both users' ids, names, current apartments,
	and each side's preference rank (1, 2, or 3).
	"""

	# Load all requests (could add filters like is_active==True as needed)
	requests = list(swap_requests_collection.find({'type': 'swap_request'}))
	matches = []
	seen_pairs = set()

	for i, req_a in enumerate(requests):
		
		user_a = str(req_a.get('user_id'))