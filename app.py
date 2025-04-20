from flask import Flask, redirect, url_for, session, jsonify, send_from_directory
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from requests_oauthlib import OAuth1
import tweepy
import os
import random
import requests
import time

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

# Twitter OAuth
twitter_bp = make_twitter_blueprint(
    api_key=os.environ.get("API_KEY"),
    api_secret=os.environ.get("API_SECRET"),
)
app.register_blueprint(twitter_bp, url_prefix="/login")

used_tags = set()

def get_next_tag():
    while True:
        tag_number = random.randint(0, 9999)
        tag = f"BC{tag_number:04d}"
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

    resp = twitter.get("account/verify_credentials.json")
    if not resp.ok:
        return jsonify({"error": "Failed to verify credentials"}), 400

    screen_name = resp.json()["screen_name"]
    token = twitter_bp.token["oauth_token"]
    token_secret = twitter_bp.token["oauth_token_secret"]

    auth = tweepy.OAuth1UserHandler(
        os.environ.get("API_KEY"),
        os.environ.get("API_SECRET"),
        token,
        token_secret
    )
    api = tweepy.API(auth)

    try:
        api.verify_credentials()
    except Exception as e:
        return jsonify({"error": "Twitter auth failed"}), 500

    cow_tag = get_next_tag()
    new_name = f"BetaCuckBot - {cow_tag} 🔞"
    new_bio = "I'm just a Beta Cuck serving @ScamBaitFindom. I'm Permanently Pussyfree for my BetaDomme 🔞 🫣 youpay.me/BetaCuckMommy647"
    new_tweet = "I'm a BetaCuckBot serving @ScamBaitFindom. Become Permanently Pussyfree! 🔞 🫣 Join me! https://bit.ly/3Gi9cOb"

    try:
        api.update_profile(name=new_name, description=new_bio)
    except tweepy.TweepyException as e:
        return jsonify({"error": f"Profile update failed: {str(e)}"}), 500

    try:
        image_url = "https://raw.githubusercontent.com/ScamBeta/twitter-profile-updater/f6193417cc8cd9500c4ea0ead93704fc5211d2e2/images/beta_belle3.jpg"
        image_path = "temp_tweet.jpg"
        img_data = requests.get(image_url).content
        with open(image_path, "wb") as f:
            f.write(img_data)

        # Upload image using v1.1 media/upload
        media = api.media_upload(image_path)
        media_id = media.media_id_string
        print(f"📸 Media uploaded with ID: {media_id}")

    except Exception as img_err:
        print(f"❌ Image upload failed: {img_err}")
        media_id = None
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

    try:
        if media_id:
            tweet_response = api.update_status(status=new_tweet, media_ids=[media_id])
        else:
            tweet_response = api.update_status(status=new_tweet)
        print(f"🐦 Tweet posted: {tweet_response.id}")
    except Exception as tweet_err:
        print(f"❌ Tweet post failed: {tweet_err}")

    return jsonify({"message": f"Updated Twitter profile for @{screen_name} with tag {cow_tag}!"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

