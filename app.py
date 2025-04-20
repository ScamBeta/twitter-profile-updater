from flask import Flask, jsonify, send_from_directory
import os
import random
import requests
import base64
import time

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

# In-memory set to track used tags
used_tags = set()

BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
USER_ID = os.environ.get("TWITTER_USER_ID")  # Get this manually from your account
IMAGE_URL = "https://raw.githubusercontent.com/ScamBeta/twitter-profile-updater/62f8ef37e895369a970f8433a00ec0eaa1cc9e2c/images/profile.jpg"

def get_next_tag():
    while True:
        tag_number = random.randint(0, 9999)
        tag = f"BC{tag_number:04d}"
        if tag not in used_tags:
            used_tags.add(tag)
            return tag

def twitter_headers():
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/update-twitter", methods=["POST"])
def update_twitter():
    cow_tag = get_next_tag()
    new_name = f"BetaCuckBot - {cow_tag} 🔞"
    new_bio = "I'm just a Beta Cuck serving @ScamBaitFindom. I'm Permanently Pussyfree for my BetaDomme 🔞 🫣 youpay.me/BetaCuckMommy647"
    new_tweet = "I'm a BetaCuckBot serving @ScamBaitFindom. Become Permanently Pussyfree! Join me!"

    try:
        print("🔄 Updating profile name and bio...")
        profile_update = requests.post(
            f"https://api.twitter.com/1.1/account/update_profile.json",
            headers=twitter_headers(),
            params={"name": new_name, "description": new_bio}
        )
        if not profile_update.ok:
            print("❌ Profile update failed:", profile_update.text)
            return jsonify({"error": "Profile update failed"}), 400
        print("✅ Profile updated.")

        print("🖼️ Uploading profile image...")
        img_data = requests.get(IMAGE_URL).content
        with open("temp.jpg", "wb") as f:
            f.write(img_data)
        with open("temp.jpg", "rb") as img:
            img_bytes = img.read()
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        media_upload = requests.post(
            "https://upload.twitter.com/1.1/account/update_profile_image.json",
            headers={
                "Authorization": f"Bearer {BEARER_TOKEN}",
            },
            files={"image": ("profile.jpg", img_bytes, "image/jpeg")}
        )
        if not media_upload.ok:
            print("❌ Image upload failed:", media_upload.text)
        else:
            print("✅ Profile image updated.")

    except Exception as e:
        print("❌ Exception during profile update:", e)

    finally:
        if os.path.exists("temp.jpg"):
            os.remove("temp.jpg")

    try:
        print("🐦 Posting tweet...")
        tweet = requests.post(
            f"https://api.twitter.com/2/tweets",
            headers=twitter_headers(),
            json={"text": new_tweet}
        )
        if not tweet.ok:
            print("❌ Tweet failed:", tweet.text)
            return jsonify({"error": "Tweet failed"}), 400
        print(f"✅ Tweet posted: {tweet.json()}")
    except Exception as e:
        print("❌ Tweet exception:", e)
        return jsonify({"error": "Tweet error"}), 500

    return jsonify({"message": f"Updated profile with tag {cow_tag}!"})

@app.route("/logout")
def logout():
    return send_from_directory("static", "login.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

