# Rutgers Room Swap - Flask Application

A web application that allows Rutgers University students to find room swap opportunities by matching their housing preferences with other students.

## Features

### 🔐 User Authentication
- **Registration**: Create accounts with Rutgers email addresses only
- **Login/Logout**: Secure authentication system
- **Session Management**: Persistent login sessions

### 📝 Room Swap Management
- **Create Requests**: Post your current housing and desired locations
- **Edit Requests**: Update your preferences anytime
- **Delete Requests**: Remove your listing when no longer needed
- **View All Requests**: Browse all active swap requests

### 🎯 Smart Matching System
- **Automatic Matching**: Find potential swaps based on mutual preferences
- **Priority Ranking**: See how well your preferences align (🥇🥈🥉)
- **Real-time Updates**: Matches update automatically when requests change

### 🏢 Supported Housing Locations
- College Avenue Apartments
- Busch Suites
- Cook Apartments
- Livingston Apartments
- Yard Apartments
- Silvers Apartments
- Easton Avenue Apartments
- Rockoff Hall
- Demarest Hall
- Campbell Hall
- Other locations

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB with PyMongo
- **Authentication**: Flask-Login
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with modern design

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- MongoDB installed and running locally

### Step 1: Install and Start MongoDB
```bash
# On macOS with Homebrew
brew install mongodb-community
brew services start mongodb-community

# On Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb

# On Windows, download from mongodb.com and start the service
```

### Step 2: Clone or Download
```bash
# If using git
git clone <repository-url>
cd RUSwapping

# Or simply download and extract the files
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

### Step 4: Access the Website
Open your browser and go to: `http://localhost:5000`

## Usage Guide

### For New Users
1. **Register**: Click "Create Account" and use your Rutgers email
2. **Create Request**: Fill out your current housing and preferences
3. **Find Matches**: View potential room swaps automatically
4. **Connect**: Contact matches via email to arrange swaps

### For Existing Users
1. **Login**: Use your email and password
2. **Manage Request**: Edit, update, or delete your listing
3. **View Matches**: Check your dashboard for new potential matches
4. **Browse All**: See all active requests from other students

## Database Structure

The application uses MongoDB with three main collections:

- **users**: User accounts and authentication
- **swap_requests**: Room swap listings and preferences
- **matches**: Automatic matching between compatible requests

## Security Features

- **Email Validation**: Only Rutgers email addresses allowed
- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Secure login sessions with Flask-Login
- **Input Validation**: Server-side validation for all forms

## File Structure

```
RUSwapping/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with styling
│   ├── home.html         # Welcome page
│   ├── register.html     # User registration
│   ├── login.html        # User login
│   └── dashboard.html    # User dashboard
└── MongoDB database      # Created automatically in MongoDB
```

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Swap Requests
- `GET /api/swap-requests` - Get all active requests
- `POST /api/swap-requests` - Create new request
- `PUT /api/swap-requests/<id>` - Update existing request
- `DELETE /api/swap-requests/<id>` - Delete request

### Matches
- `GET /api/matches` - Get user's potential matches

## Customization

### Adding New Housing Locations
Edit the housing options in:
- `templates/dashboard.html` (form options)
- `templates/home.html` (displayed locations)

### Styling Changes
Modify the CSS in `templates/base.html` to change colors, fonts, and layout.

### Database Modifications
The database schema is defined in `app.py` using MongoDB collections. The database and collections are created automatically when you first run the application.

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change port in app.py
   app.run(debug=True, port=5001)
   ```

2. **Database Errors**
   ```bash
   # Clear MongoDB collections and restart
   mongo roomswap_db --eval "db.users.drop(); db.swap_requests.drop(); db.matches.drop()"
   python app.py
   ```

3. **Import Errors**
   ```bash
   # Ensure all dependencies are installed
   pip install -r requirements.txt
   ```

### Getting Help
- Check the browser console for JavaScript errors
- Review Flask application logs in the terminal
- Ensure all required files are in the correct directories

## Future Enhancements

Potential features for future versions:
- Email notifications for new matches
- Advanced filtering and search
- Roommate compatibility scoring
- Photo uploads for rooms
- Mobile app version
- Integration with Rutgers housing system

## License

This project is created for educational purposes and Rutgers University students.

## Support

For questions or issues, please check the troubleshooting section above or review the code comments for guidance. 