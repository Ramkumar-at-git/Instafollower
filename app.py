import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS  # Import CORS
import instaloader
import logging
import requests
import time

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Initialize Instaloader
L = instaloader.Instaloader()

# Configure logging to get more insights in case of errors
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/followers')
def get_followers():
    # Get the username from query parameters
    username = request.args.get('username')
    
    # If no username is provided, return an error
    if not username:
        return jsonify({'error': 'Username parameter is required.'})

    try:
        # Load the profile
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Get the follower count
        followers = profile.followers
        
        return jsonify({'followers': followers})
    
    except instaloader.exceptions.ProfileNotExistsException:
        # If the profile doesn't exist
        logging.error(f"Profile {username} does not exist.")
        return jsonify({'error': 'Profile does not exist.'})
    
    except instaloader.exceptions.PrivateProfileNotAccessibleException:
        # If the profile is private and inaccessible
        logging.error(f"Profile {username} is private or inaccessible.")
        return jsonify({'error': 'Profile is private or inaccessible.'})
    
    except instaloader.exceptions.InstaloaderException as e:
        # General Instaloader exceptions (e.g., network error)
        logging.error(f"Instaloader exception: {str(e)}")
        return jsonify({'error': f'Error fetching follower count: {str(e)}'})
    
    except requests.exceptions.RequestException as e:
        # Handle network errors with requests (e.g., network issues)
        logging.error(f"Network error: {str(e)}")
        return jsonify({'error': 'Network error. Please try again later.'})
    
    except Exception as e:
        # Catch any other exceptions
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'})

# Main entry point for running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
