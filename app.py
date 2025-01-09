import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import instaloader
import requests

app = Flask(__name__)

# Enable CORS for all routes (adjust the origins if needed)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Instaloader
L = instaloader.Instaloader()

# Configure logging to get more insights in case of errors
logging.basicConfig(level=logging.INFO)

# Instagram login credentials (to be provided via form input)
INSTAGRAM_USERNAME = None
INSTAGRAM_PASSWORD = None

# Path to store session cookies
SESSION_FILE_PATH = "insta_session.json"

# Function to load the session or perform login
def load_instagram_session():
    global INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

    try:
        # Load the session from file if available
        L.load_session_from_file(INSTAGRAM_USERNAME)  # Try loading session from a file
        logging.info(f"Session loaded for {INSTAGRAM_USERNAME}")
    except FileNotFoundError:
        # If no session file exists, log in and save the session
        logging.info("No session found, logging in with username and password.")
        try:
            L.context.log(f"Logging in as {INSTAGRAM_USERNAME}...")
            L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            L.save_session_to_file()  # Save the session for future use
            logging.info("Session saved successfully!")
        except instaloader.exceptions.LoginException as e:
            logging.error(f"Login failed: {str(e)}")
            return False
    except instaloader.exceptions.LoginRequiredException:
        logging.error("Login required for Instagram.")
        return False

    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

    if request.method == 'POST':
        INSTAGRAM_USERNAME = request.form['username']
        INSTAGRAM_PASSWORD = request.form['password']
        
        # Attempt to load the Instagram session
        success = load_instagram_session()

        if success:
            message = f"Successfully logged in as {INSTAGRAM_USERNAME}!"
            return render_template('login.html', message=message)
        else:
            message = "Login failed. Please check your credentials."
            return render_template('login.html', message=message)

    return render_template('login.html')

@app.route('/followers')
def get_followers():
    username = request.args.get('username')

    if not username:
        logging.error("Username parameter is missing.")
        return jsonify({'error': 'Username parameter is required.'})

    try:
        # Fetch the profile
        logging.info(f"Fetching followers for username: {username}")

        # Make sure the session is loaded first
        if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
            success = load_instagram_session()
            if not success:
                return jsonify({'error': 'Login required. Please log in to Instagram.'})

        # Load the profile and get follower count
        profile = instaloader.Profile.from_username(L.context, username)
        followers = profile.followers

        logging.info(f"Found {followers} followers for {username}")
        return jsonify({'followers': followers})

    except instaloader.exceptions.ProfileNotExistsException:
        logging.error(f"Profile {username} does not exist.")
        return jsonify({'error': 'Profile does not exist.'})

    except instaloader.exceptions.LoginRequiredException:
        logging.error("Login required.")
        return jsonify({'error': 'Login required. Please log in to Instagram.'})

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error: {str(e)}")
        return jsonify({'error': 'Network error. Please try again later.'})

    except instaloader.exceptions.InstaloaderException as e:
        logging.error(f"Instaloader error: {str(e)}")
        return jsonify({'error': f'Error with Instaloader: {str(e)}'})

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'})

# Main entry point for running the app
if __name__ == '__main__':
    # Log the startup message
    logging.info("Starting Flask app on port 5000.")

    # Run the Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
