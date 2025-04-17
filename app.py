from flask import Flask, redirect, request, jsonify, session
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

# Spotify Credentials
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "https://your-app-name.onrender.com/spotify/callback"

# Strava Credentials
STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = "https://your-app-name.onrender.com/strava/callback"

# Spotify OAuth
@app.route("/spotify/login")
def spotify_login():
    auth_url = ("https://accounts.spotify.com/authorize?"
                f"client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}"
                "&scope=playlist-modify-public playlist-modify-private user-top-read")
    return redirect(auth_url)

@app.route("/spotify/callback")
def spotify_callback():
    code = request.args.get("code")
    res = requests.post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    })
    session['spotify_token'] = res.json().get("access_token")
    return redirect("/dashboard")

# Strava OAuth
@app.route("/strava/login")
def strava_login():
    auth_url = ("https://www.strava.com/oauth/authorize?"
                f"client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri={STRAVA_REDIRECT_URI}"
                "&approval_prompt=auto&scope=activity:read_all")
    return redirect(auth_url)

@app.route("/strava/callback")
def strava_callback():
    code = request.args.get("code")
    res = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    })
    session['strava_token'] = res.json().get("access_token")
    return redirect("/dashboard")

# Dashboard Placeholder
@app.route("/dashboard")
def dashboard():
    return "OAuth complete! Ready to fetch run + music data."

# Get Most Recent Strava Run
@app.route("/strava/recent_run")
def get_recent_run():
    token = session.get('strava_token')
    headers = {"Authorization": f"Bearer {token}"}
    activities = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers).json()
    for activity in activities:
        if activity['type'] == 'Run':
            return jsonify(activity)
    return jsonify({"error": "No runs found."})

# Create Spotify Playlist (Placeholder)
@app.route("/spotify/create_playlist", methods=['POST'])
def create_playlist():
    token = session.get('spotify_token')
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    user_profile = requests.get("https://api.spotify.com/v1/me", headers=headers).json()
    user_id = user_profile['id']

    playlist_data = {
        "name": "Runner's High Custom Playlist",
        "description": "Made for your route & pace!",
        "public": False
    }

    playlist_res = requests.post(f"https://api.spotify.com/v1/users/{user_id}/playlists",
                                 headers=headers, json=playlist_data)
    return jsonify(playlist_res.json())

if __name__ == '__main__':
    app.run(debug=True)
