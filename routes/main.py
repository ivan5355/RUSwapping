import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from routes.auth import auth, login_required
from routes.preference_swapping_requests import pref_swap_requests_bp
from routes.cycle_swapping_requests import cycle_swapping_requests_bp
import os
from routes.auth import get_current_user
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
main = Flask(__name__, static_folder='../static', template_folder='../templates')

# Secret key used for session cookies (loaded from env with a dev fallback)
main.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

# Register authentication routes (login, register, logout)
main.register_blueprint(auth)

# Register swap requests blueprint
main.register_blueprint(pref_swap_requests_bp)

# Register cycle requests blueprint
main.register_blueprint(cycle_swapping_requests_bp)

@main.route('/')
def home():
	"""Render the public home page."""
	return render_template('home.html')

@main.route('/dashboard')
@login_required
def dashboard():
	"""Redirect to preference swapping page (legacy support)."""
	return redirect(url_for('preference_swapping'))

@main.route('/preference-swapping')
@login_required
def preference_swapping():
	"""Render the preference-based swapping page."""
	return render_template('preference_swapping.html')

@main.route('/cycle-swapping')
@login_required
def cycle_swapping():
	"""Render the cycle swapping page."""
	return render_template('cycle_swapping.html')

def show_requests():
	"""Show all requests."""

	requests = swap_requests_collection.find({'type': 'swap_request'})
	for request in requests:
		print(request)

