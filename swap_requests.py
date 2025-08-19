from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from auth import login_required, get_current_user
import os

load_dotenv()

# MongoDB connection (kept local to avoid circular imports)
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=20000)
db = client["RUSwapping"]

swap_requests_collection = db['swap_requests']

swap_requests_bp = Blueprint('swap_requests', __name__)

@swap_requests_bp.route('/create-request', methods=['POST'])
@login_required
def create_request():
	"""Create a new swap request for the current user."""
	current_user = get_current_user()
	request_data = request.get_json(silent=True) or request.form
	if not request_data:
		return jsonify({'error': 'Invalid or missing request payload'}), 400

	current_apartment = request_data.get('current_apartment')
	current_room = request_data.get('current_room', '')
	first_choice = request_data.get('first_choice')
	second_choice = request_data.get('second_choice')
	third_choice = request_data.get('third_choice')

	if not current_apartment or not first_choice or not second_choice or not third_choice:
		return jsonify({'error': 'All fields are required'}), 400

	existing_request = swap_requests_collection.find_one({
		'user_id': current_user['id'],
		'type': 'swap_request'
	})
	if existing_request:
		return jsonify({'error': 'You already have a swap request. Please delete your existing request first or update it.'}), 400

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

	res = swap_requests_collection.insert_one(doc)
	return jsonify({'message': 'Swap request created successfully!', 'request_id': str(res.inserted_id)}), 201

@swap_requests_bp.route('/delete-request', methods=['POST'])
@login_required
def delete_request():
	"""Delete a swap request for the current user."""
	request_data = request.get_json(silent=True) or request.form
	request_id = request_data.get('request_id')
	if not request_id:
		return jsonify({'error': 'request_id is required'}), 400
	current_user = get_current_user()
	result = swap_requests_collection.delete_one({'_id': ObjectId(request_id), 'user_id': current_user['id'], 'type': 'swap_request'})
	if result.deleted_count == 0:
		return jsonify({'error': 'Request not found or not authorized'}), 404
	return jsonify({'message': 'Swap request deleted successfully!'}), 200

@swap_requests_bp.route('/update-request', methods=['POST'])
@login_required
def update_request():
	"""Update a swap request for the current user."""
	request_data = request.get_json(silent=True)
	if not request_data:
		return jsonify({'error': 'Invalid or missing request payload'}), 400

	request_id = request_data.get('request_id')
	if not request_id:
		return jsonify({'error': 'request_id is required'}), 400

	current_user = get_current_user()
	existing_request = swap_requests_collection.find_one({'_id': ObjectId(request_id), 'user_id': current_user['id'], 'type': 'swap_request'})
	if not existing_request:
		return jsonify({'error': 'Request not found or not authorized'}), 404

	current_apartment = request_data.get('current_apartment')
	first_choice = request_data.get('first_choice')
	second_choice = request_data.get('second_choice')
	third_choice = request_data.get('third_choice')

	update_data = {}
	if current_apartment is not None:
		update_data['current_apartment'] = current_apartment
	if 'current_room' in request_data:
		update_data['current_room'] = request_data.get('current_room', '')
	if any(v is not None for v in [first_choice, second_choice, third_choice]):
		prefs = existing_request.get('preferences', {})
		if first_choice is not None:
			prefs['first_choice'] = first_choice
		if second_choice is not None:
			prefs['second_choice'] = second_choice
		if third_choice is not None:
			prefs['third_choice'] = third_choice
		update_data['preferences'] = prefs

	if not update_data:
		return jsonify({'error': 'No updatable fields provided'}), 400

	update_data['updated_at'] = datetime.utcnow()
	result = swap_requests_collection.update_one({'_id': ObjectId(request_id), 'user_id': current_user['id']}, {'$set': update_data})
	if result.modified_count > 0:
		return jsonify({'message': 'Swap request updated successfully!'}), 200
	else:
		return jsonify({'message': 'No changes applied'}), 200 

@swap_requests_bp.route('/get-requests', methods=['GET'])
@login_required
def get_request():
	"""Return the current user's active swap request."""
	current_user = get_current_user()
	user_request = swap_requests_collection.find_one({
		'user_id': current_user['id'],
		'type': 'swap_request'
	})
	if user_request:
		user_request['is_own'] = True
		# Convert ObjectId to str and nested types
		from utils.utils import to_jsonable
		return jsonify([to_jsonable(user_request)])
	else:
		return jsonify([]) 

@swap_requests_bp.route('/delete-requests/<request_id>', methods=['DELETE'])
@login_required
def delete_swap_request(request_id):
	"""Delete a swap request permanently (matches frontend DELETE call)."""

	current_user = get_current_user()
	result = swap_requests_collection.delete_one({'_id': ObjectId(request_id), 'user_id': current_user['id'], 'type': 'swap_request'})

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