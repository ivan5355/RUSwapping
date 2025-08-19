# RUSwapping - Setup Guide

## Prerequisites
- Python 3.10+
- MongoDB (local on `mongodb://localhost:27017/` or MongoDB Atlas)

## 1) Create virtual environment
- macOS/Linux:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
- Windows (PowerShell):
  - `py -3 -m venv .venv`
  - `.venv\Scripts\Activate.ps1`

## 2) Install dependencies
- `pip install -r requirements.txt`

## 3) Configure environment
Create a `.env` file in the project root with:
```
MONGO_URI=mongodb://localhost:27017/
SECRET_KEY=dev-secret
```
- Use your MongoDB Atlas URI if not running local MongoDB.

## 4) Run the app
- `python app.py`
- Visit `http://127.0.0.1:5000/`

## 5) Use the app
- Register with your Rutgers `@scarletmail.rutgers.edu` email
- Log in
- Create your swap request on the Dashboard
- See mutual matches under "Your Matches"

## Notes
- If using local MongoDB, ensure it is running before starting the app.
- You can change `SECRET_KEY` to any random string in production. 