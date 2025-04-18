from flask import Flask, redirect, url_for, session, jsonify, send_from_directory
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import tweepy
import os
import random

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

    cow_tag = get_next_tag()
    new_name = f"BetaCuckBot - {cow_tag} 🔞"

    try:
        api.update_profile(name=new_name, description=f"I'm just a Beta Cuck serving @ScamBaitFindom I'm Permanently Pussyfree for my BetaDomme 🔞 🫣 youpay.me/BetaCuckMommy647 ")
        with open("profile.jpg", "rb") as f:
            api.update_profile_image(filename="profile.jpg", file=f)
        api.update_status(f"I'm a BetaCuckBot serving @ScamBaitFindom  Become Permanently Pussyfree!  Join me! ")

        return jsonify({"message": f"Updated Twitter profile for @{screen_name} with tag {cow_tag}!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
