from flask import Flask, redirect, request, session, url_for
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# === Spotify Config ===
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "https://yourapp.onrender.com/spotify/callback"
SPOTIFY_SCOPE = "playlist-modify-public"

# === Strava Config ===
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = "https://yourapp.onrender.com/strava/callback"

@app.route("/")
def home():
    return """
    <h2>Welcome to Runners High 🏃‍♂️</h2>
    <a href="/login/spotify">Login with Spotify</a><br><br>
    <a href="/login/strava">Login with Strava</a>
    """

# ------------------ SPOTIFY ------------------

@app.route("/login/spotify")
def login_spotify():
    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={SPOTIFY_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={SPOTIFY_REDIRECT_URI}"
        f"&scope={SPOTIFY_SCOPE}"
    )
    return redirect(auth_url)

@app.route("/spotify/callback")
def spotify_callback():
    code = request.args.get("code")
    token_url = "https://accounts.spotify.com/api/token"
    response = requests.post(token_url, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    })

    data = response.json()
    access_token = data['access_token']
    session['spotify_token'] = access_token

    return f"<h3>✅ Spotify connected!</h3><p>Token: {access_token[:20]}...</p>"

# ------------------ STRAVA ------------------

@app.route("/login/strava")
def login_strava():
    auth_url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={STRAVA_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={STRAVA_REDIRECT_URI}"
        f"&scope=activity:read_all"
        f"&approval_prompt=force"
    )
    return redirect(auth_url)

@app.route("/strava/callback")
def strava_callback():
    code = request.args.get("code")
    token_url = "https://www.strava.com/oauth/token"
    response = requests.post(token_url, data={
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    })

    data = response.json()
    access_token = data['access_token']
    session['strava_token'] = access_token

    return f"<h3>✅ Strava connected!</h3><p>Token: {access_token[:20]}...</p>"

if __name__ == "__main__":
    app.run(debug=True)
