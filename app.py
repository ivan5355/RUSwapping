import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from auth import auth, login_required
from preference_swapping_requests import pref_swap_requests_bp
from cycle_swapping_requests import cycle_swapping_requests_bp
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
app.register_blueprint(pref_swap_requests_bp)

# Register cycle requests blueprint
app.register_blueprint(cycle_swapping_requests_bp)

@app.route('/')
def home():
	"""Render the public home page."""
	return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
	"""Redirect to preference swapping page (legacy support)."""
	return redirect(url_for('preference_swapping'))

@app.route('/preference-swapping')
@login_required
def preference_swapping():
	"""Render the preference-based swapping page."""
	return render_template('preference_swapping.html')

@app.route('/cycle-swapping')
@login_required
def cycle_swapping():
	"""Render the cycle swapping page."""
	return render_template('cycle_swapping.html')

def show_requests():
	"""Show all requests."""

	requests = swap_requests_collection.find({'type': 'swap_request'})
	for request in requests:
		print(request)

if __name__ == '__main__':
	show_requests()
	app.run(host='0.0.0.0', port=3000, debug=True) 