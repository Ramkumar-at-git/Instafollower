from flask import Flask, request, jsonify, render_template
import instaloader

app = Flask(__name__)

def get_follower_count_instaloader(username):
    try:
        loader = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(loader.context, username)
        return {"followers": profile.followers}
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')  # Ensure index.html is in the templates/ folder

@app.route('/followers', methods=['GET'])
def get_followers():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400

    result = get_follower_count_instaloader(username)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)