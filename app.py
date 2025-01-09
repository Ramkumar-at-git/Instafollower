import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS  # Import CORS
import instaloader
import logging
import requests

app = Flask(__name__)

# Enable CORS for all routes (adjust the origins if needed)
CORS(app, resources={r"/*": {"origins": "https://instafollower-47tw.onrender.com"}})

# Initialize Instaloader
L = instaloader.Instaloader()

# Configure logging to get more insights in case of errors
logging.basicConfig(level=logging.INFO)

# Instagram login credentials (replace with your own credentials for private profiles)
INSTAGRAM_USERNAME = "not12_334"
INSTAGRAM_PASSWORD = "Ramkumar@41"

# Define the session path
SESSION_PATH = f'/tmp/.instaloader-render/session-{INSTAGRAM_USERNAME}'

# Try to log in automatically when the server starts (optional, but helps with accessing private profiles)
try:
    logging.info("Attempting to load session.")
    L.load_session_from_file(INSTAGRAM_USERNAME)  # Try loading session if previously saved
except FileNotFoundError:
    logging.info("No session found, logging in with username and password.")
    try:
        # Log in with username and password
        logging.info(f"Logging in as {INSTAGRAM_USERNAME}...")
        L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)  # Login using username and password
        # Save the session to avoid logging in every time
        L.save_session_to_file()  
        logging.info("Session saved.")
    except instaloader.exceptions.LoginException as e:
        logging.error(f"Login failed: {str(e)}")
        raise
except Exception as e:
    logging.error(f"Error during session loading: {str(e)}")
    raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/followers')
def get_followers():
    # Get the username from query parameters
    username = request.args.get('username')
    
    # If no username is provided, return an error
    if not username:
        logging.error("Username parameter is missing.")
        return jsonify({'error': 'Username parameter is required.'})

    try:
        # Log the username to check if it is being passed correctly
        logging.info(f"Fetching followers for username: {username}")

        # Load the profile
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Get the follower count
        followers = profile.followers

        # Log the follower count for debugging purposes
        logging.info(f"Found {followers} followers for {username}")
        
        return jsonify({'followers': followers})
    
    except instaloader.exceptions.ProfileNotExistsException:
        logging.error(f"Profile {username} does not exist.")
        return jsonify({'error': 'Profile does not exist.'})
    
    except instaloader.exceptions.LoginRequiredException:
        logging.error(f"Login required for username: {username}.")
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
    
    # Running the Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
