from flask import Flask, redirect, url_for, session, jsonify, send_from_directory
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import tweepy
import os
import random
import requests
import base64

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

# Twitter OAuth
twitter_bp = make_twitter_blueprint(
    api_key=os.environ.get("API_KEY"),
    api_secret=os.environ.get("API_SECRET"),
)
app.register_blueprint(twitter_bp, url_prefix="/login")

# In-memory set to track used tags
used_tags = set()

def get_next_tag():
    while True:
        tag_number = random.randint(0, 9999)
        tag = f"BC{tag_number:04d}"  # e.g., BC0429
        if tag not in used_tags:
            used_tags.add(tag)
            return tag

@app.route("/")
def index():
    if not twitter.authorized:
        return send_from_directory("static", "login.html")
    return send_from_directory("static", "index.html")

@app.route("/update-twitter", methods=["POST"])
def update_twitter():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))

    # Get user info from Flask-Dance
    resp = twitter.get("account/verify_credentials.json")
    if not resp.ok:
        return jsonify({"error": "Failed to verify credentials"}), 400

    screen_name = resp.json()["screen_name"]
    token = twitter_bp.token["oauth_token"]
    token_secret = twitter_bp.token["oauth_token_secret"]

    # Set up Tweepy
    auth = tweepy.OAuth1UserHandler(
        os.environ.get("API_KEY"),
        os.environ.get("API_SECRET"),
        token,
        token_secret
    )
    api = tweepy.API(auth)

    cow_tag = get_next_tag()
    new_name = f"BetaCuckBot - {cow_tag} 🔞"
    new_bio = "I'm just a Beta Cuck serving @ScamBaitFindom. I'm Permanently Pussyfree for my BetaDomme 🔞 🫣 youpay.me/BetaCuckMommy647"
    new_tweet = "I'm a BetaCuckBot serving @ScamBaitFindom. Become Permanently Pussyfree! Join me!"

    try:
        # Update profile name and bio
        api.update_profile(name=new_name, description=new_bio)

        # Load JPEG image from web instead of disk
        image_url = "https://i.imgur.com/WzzklgP.jpg"
        img_data = requests.get(image_url).content

        # Save image temporarily
        try:
         with open("temp_profile.jpg", "rb") as f:
          api.update_profile_image(filename="temp_profile.jpg", file=f)
        except Exception as img_err:
          print(f"Image upload failed: {img_err}")

        # Upload profile image
        with open("temp_profile.jpg", "rb") as f:
            api.update_profile_image(filename="temp_profile.jpg", file=f)

        # Post tweet
        api.update_status(new_tweet)

        return jsonify({"message": f"Updated Twitter profile for @{screen_name} with tag {cow_tag}!"})

    except Exception as e:
        print(f"Error during Twitter update: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
