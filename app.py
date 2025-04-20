from flask import Flask, redirect, url_for, session, jsonify, send_from_directory
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import tweepy
import os
import random
import requests
import base64
import time

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
        print("❌ Could not verify credentials.")
        return jsonify({"error": "Failed to verify credentials"}), 400

    screen_name = resp.json()["screen_name"]
    token = twitter_bp.token["oauth_token"]
    token_secret = twitter_bp.token["oauth_token_secret"]

    print(f"🔑 OAuth token: {token}")
    print(f"🔐 OAuth secret: {token_secret}")
    print(f"👤 Screen name: {screen_name}")

    # Set up Tweepy
    auth = tweepy.OAuth1UserHandler(
        os.environ.get("API_KEY"),
        os.environ.get("API_SECRET"),
        token,
        token_secret
    )
    api = tweepy.API(auth)

    try:
        api.verify_credentials()
        print("✅ Tweepy authentication succeeded.")
    except Exception as e:
        print("❌ Tweepy authentication failed:", e)
        return jsonify({"error": "Twitter auth failed"}), 500

    cow_tag = get_next_tag()
    new_name = f"BetaCuckBot - {cow_tag} 🔞"
    new_bio = "I'm just a Beta Cuck serving @ScamBaitFindom. I'm Permanently Pussyfree for my BetaDomme 🔞 🫣 youpay.me/BetaCuckMommy647"
    new_tweet = "I'm a BetaCuckBot serving @ScamBaitFindom. Become Permanently Pussyfree! Join me!"

    print("🔄 Updating profile...")
    time.sleep(2)

    # Update profile name and bio
    try:
        response = api.update_profile(name=new_name, description=new_bio)
        print(f"✅ Profile updated: {response}")
    except tweepy.TweepyException as e:
        print("❌ Profile update error:", e)
        if hasattr(e, 'response') and e.response is not None:
            print("📨 Twitter API response body:", e.response.text)
        return jsonify({"error": f"Profile update failed: {str(e)}"}), 500

    # Upload profile image
    try:
        image_url = "https://raw.githubusercontent.com/ScamBeta/twitter-profile-updater/62f8ef37e895369a970f8433a00ec0eaa1cc9e2c/images/profile.jpg"
        image_path = "temp_profile.jpg"

        # Download image
        img_data = requests.get(image_url).content
        with open(image_path, "wb") as f:
            f.write(img_data)

        # Upload to Twitter
        with open(image_path, "rb") as f:
            api.update_profile_image(filename=image_path, file=f)
        print("🖼️ Profile image updated.")

    except Exception as img_err:
        print(f"❌ Image upload failed: {img_err}")

    finally:
        # Clean up temp file
        if os.path.exists(image_path):
            os.remove(image_path)
            print("🧹 Temp file removed.")

    # Tweet new status
from requests_oauthlib import OAuth1

# Tweet new status using Twitter API v2
try:
    url = "https://api.twitter.com/2/tweets"
    payload = {"text": new_tweet}

    auth = OAuth1(
        os.environ.get("API_KEY"),
        os.environ.get("API_SECRET"),
        token,
        token_secret
    )

    response = requests.post(url, json=payload, auth=auth)

    if response.status_code == 201:
        tweet_id = response.json()["data"]["id"]
        print(f"🐦 Tweet posted via v2: {tweet_id}")
    else:
        print(f"❌ Failed to tweet via v2: {response.status_code}")
        print("📨 Response:", response.text)

except Exception as tweet_err:
    print(f"❌ Tweet post (v2) failed: {tweet_err}")


    return jsonify({"message": f"Updated Twitter profile for @{screen_name} with tag {cow_tag}!"})



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
