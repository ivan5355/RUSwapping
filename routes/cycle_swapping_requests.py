from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from routes.auth import login_required, get_current_user
import os

load_dotenv()

# MongoDB connection (kept local to avoid circular imports)
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=20000)
db = client["RUSwapping"]

swap_requests_collection = db['swap_requests']
users_collection = db['users']

cycle_swapping_requests_bp = Blueprint('cycle_swapping_requests', __name__)

@cycle_swapping_requests_bp.route('/create-cycle-request', methods=['POST'])
@login_required
def create_cycle_request():

	"""Create a new cycle request (single desired choice) for the current user."""
	current_user = get_current_user()
	request_data = request.get_json(silent=True) 

	if not request_data:
		return jsonify({'error': 'Invalid or missing request payload'}), 400

	current_apartment = request_data.get('current_apartment')
	current_room = request_data.get('current_room', '')
	desired_choice = request_data.get('desired_choice')

	if not current_apartment or not desired_choice:
		return jsonify({'error': 'current_apartment and desired_choice are required'}), 400

	existing_request = swap_requests_collection.find_one({
		'user_id': current_user['id'],
		'type': 'cycle_request'
	})
	if existing_request:
		return jsonify({'error': 'You already have a cycle request. Please delete your existing cycle request first or update it.'}), 400

	doc = {
		'user_id': current_user['id'],
		'user_name': current_user['name'],
		'current_apartment': current_apartment,
		'current_room': current_room,
		'desired_choice': desired_choice,
		'created_at': datetime.utcnow(),
		'type': 'cycle_request'
	}

	res = swap_requests_collection.insert_one(doc)
    
	return jsonify({'message': 'Cycle swap request created successfully!', 'request_id': str(res.inserted_id)}), 201

@cycle_swapping_requests_bp.route('/update-cycle-request', methods=['POST'])
@login_required
def update_cycle_request():
	"""Update the current user's cycle request."""
	request_data = request.get_json(silent=True)
	if not request_data:
		return jsonify({'error': 'Invalid or missing request payload'}), 400

	request_id = request_data.get('request_id')
	if not request_id:
		return jsonify({'error': 'request_id is required'}), 400

	current_user = get_current_user()
	existing_request = swap_requests_collection.find_one({'_id': ObjectId(request_id), 'user_id': current_user['id'], 'type': 'cycle_request'})
	if not existing_request:
		return jsonify({'error': 'Request not found or not authorized'}), 404

	update_data = {}
	if 'current_apartment' in request_data:
		update_data['current_apartment'] = request_data.get('current_apartment')
	if 'current_room' in request_data:
		update_data['current_room'] = request_data.get('current_room', '')
	if 'desired_choice' in request_data:
		update_data['desired_choice'] = request_data.get('desired_choice')

	if not update_data:
		return jsonify({'error': 'No updatable fields provided'}), 400

	update_data['updated_at'] = datetime.utcnow()
	result = swap_requests_collection.update_one({'_id': ObjectId(request_id), 'user_id': current_user['id']}, {'$set': update_data})
	if result.modified_count > 0:
		return jsonify({'message': 'Cycle swap request updated successfully!'}), 200
	else:
		return jsonify({'message': 'No changes applied'}), 200

@cycle_swapping_requests_bp.route('/get-cycle-requests', methods=['GET'])
@login_required
def get_cycle_request():
	"""Return the current user's active cycle request."""
	current_user = get_current_user()
	user_request = swap_requests_collection.find_one({
		'user_id': current_user['id'],
		'type': 'cycle_request'
	})
	if user_request:
		user_request['is_own'] = True
		from utils.utils import to_jsonable
		return jsonify([to_jsonable(user_request)])
	else:
		return jsonify([])

@cycle_swapping_requests_bp.route('/delete-cycle-requests/<request_id>', methods=['DELETE'])
@login_required
def delete_cycle_request(request_id):

	"""Delete a cycle request permanently."""
	current_user = get_current_user()
	result = swap_requests_collection.delete_one({'_id': ObjectId(request_id), 'user_id': current_user['id'], 'type': 'cycle_request'})
	if result.deleted_count == 0:
		return jsonify({'error': 'Request not found or not authorized'}), 404
	return jsonify({'message': 'Cycle swap request deleted successfully'}), 200

@cycle_swapping_requests_bp.route('/get-cycle-matches', methods=['GET'])
@login_required
def get_cycle_matches():
	"""Get cycle matches for the current user (direct swaps first, then 3-way chains)."""
	current_user = get_current_user()
	if not current_user:
		return jsonify([])

	# Fetch current user's active cycle request
	my_request = swap_requests_collection.find_one({
		'user_id': current_user['id'],
		'type': 'cycle_request'
	})
	if not my_request:
		return jsonify([])

	my_current_apartment = my_request.get('current_apartment')
	my_desired_choice = my_request.get('desired_choice')

	matches = []

	# First, look for direct 2-way swaps
	for other_request in swap_requests_collection.find({'type': 'cycle_request'}):
		# Skip own document
		if other_request.get('user_id') == current_user['id']:
			continue

		other_current_apartment = other_request.get('current_apartment')
		other_desired_choice = other_request.get('desired_choice')

		# Direct swap: I want their place, they want my place
		if (my_desired_choice == other_current_apartment and 
			other_desired_choice == my_current_apartment):
			
			other_user_email_display = other_request.get('user_email_display') or other_request.get('email', '')
			if not other_user_email_display:
				try:
					other_user_id_str = other_request.get('user_id')
					if other_user_id_str:
						other_user_doc = users_collection.find_one({'_id': ObjectId(other_user_id_str)})
						if other_user_doc:
							other_user_email_display = other_user_doc.get('email', '')
				except Exception:
					pass

			matches.append({
				'other_user_id': other_request.get('user_id') or str(other_request.get('_id')),
				'other_user_name': other_request.get('user_name') or other_request.get('name', ''),
				'other_current_apartment': other_current_apartment,
				'other_current_room': other_request.get('current_room', ''),
				'match_type': 'direct_swap',
				'other_user_email_display': other_user_email_display
			})

	# If no direct swaps, look for 3-way chains
	if not matches:
		for other_request in swap_requests_collection.find({'type': 'cycle_request'}):
			# Skip own document
			if other_request.get('user_id') == current_user['id']:
				continue

			other_current_apartment = other_request.get('current_apartment')
			other_desired_choice = other_request.get('desired_choice')

			# Look for a third person to complete the chain
			for third_request in swap_requests_collection.find({'type': 'cycle_request'}):
				# Skip own document and the second person
				if (third_request.get('user_id') == current_user['id'] or 
					third_request.get('user_id') == other_request.get('user_id')):
					continue

				third_current_apartment = third_request.get('current_apartment')
				third_desired_choice = third_request.get('desired_choice')

				# Check if this forms a 3-way chain:
				# I want other's place, other wants third's place, third wants my place
				if (my_desired_choice == other_current_apartment and
					other_desired_choice == third_current_apartment and
					third_desired_choice == my_current_apartment):
					
					other_user_email_display = other_request.get('user_email_display') or other_request.get('email', '')
					third_user_email_display = third_request.get('user_email_display') or third_request.get('email', '')
					
					if not other_user_email_display:
						try:
							other_user_id_str = other_request.get('user_id')
							if other_user_id_str:
								other_user_doc = users_collection.find_one({'_id': ObjectId(other_user_id_str)})
								if other_user_doc:
									other_user_email_display = other_user_doc.get('email', '')
						except Exception:
							pass

					if not third_user_email_display:
						try:
							third_user_id_str = third_request.get('user_id')
							if third_user_id_str:
								third_user_doc = users_collection.find_one({'_id': ObjectId(third_user_id_str)})
								if third_user_doc:
									third_user_email_display = third_user_doc.get('email', '')
						except Exception:
							pass

					matches.append({
						'other_user_id': other_request.get('user_id') or str(other_request.get('_id')),
						'other_user_name': other_request.get('user_name') or other_request.get('name', ''),
						'other_current_apartment': other_current_apartment,
						'other_current_room': other_request.get('current_room', ''),
						'third_user_id': third_request.get('user_id') or str(third_request.get('_id')),
						'third_user_name': third_request.get('user_name') or third_request.get('name', ''),
						'third_current_apartment': third_current_apartment,
						'third_current_room': third_request.get('current_room', ''),
						'match_type': 'three_way_chain',
						'other_user_email_display': other_user_email_display,
						'third_user_email_display': third_user_email_display
					})
					break  # Found a match, no need to look for more third parties

	return jsonify(matches) 