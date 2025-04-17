from flask import Flask, jsonify, send_from_directory
import tweepy, os

app = Flask(__name__, static_folder='static')

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/update-twitter', methods=['POST'])
def update_twitter():
    try:
        api.update_profile(name="FlaskBot 😎", description="Updated via Flask on Render!")
        with open("profile.jpg", "rb") as image_file:
            api.update_profile_image(filename="profile.jpg", file=image_file)
        api.update_status("Profile updated using Flask + Render! 🚀")
        return jsonify({"message": "Twitter updated!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
