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
@app.route("/strava/activities")
def strava_activities():
    access_token = session.get('strava_token')
    if not access_token:
        return redirect(url_for('login_strava'))

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get("https://www.strava.com/api/v3/athlete/activities", headers=headers)

    if response.status_code != 200:
        return "⚠️ Error getting activities", 400

    activities = response.json()

    # Find the latest RUN (not ride, etc.)
    for act in activities:
        if act['type'] == 'Run':
            distance_km = act['distance'] / 1000
            elevation_gain = act['total_elevation_gain']
            name = act['name']
            moving_time = act['moving_time']  # in seconds
            break
    else:
        return "No runs found"

    return f"""
        <h3>Latest Run: {name}</h3>
        <p>Distance: {distance_km:.2f} km</p>
        <p>Elevation Gain: {elevation_gain:.2f} m</p>
        <p>Time: {moving_time / 60:.1f} minutes</p>
        <a href='/create_playlist'>Create Spotify Playlist for this run</a>
    """

    data = response.json()
    access_token = data['access_token']
    session['strava_token'] = access_token

    return f"<h3>✅ Strava connected!</h3><p>Token: {access_token[:20]}...</p>"

@app.route("/create_playlist")
def create_playlist():
    access_token = session.get('spotify_token')
    if not access_token:
        return redirect(url_for('login_spotify'))

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # 1. Create a playlist
    user_profile = requests.get("https://api.spotify.com/v1/me", headers=headers).json()
    user_id = user_profile["id"]

    playlist_data = {
        "name": "Runner's High: Elevation Mix",
        "description": "Custom BPM playlist for your last run",
        "public": True
    }

    playlist = requests.post(
        f"https://api.spotify.com/v1/users/{user_id}/playlists",
        json=playlist_data,
        headers=headers
    ).json()

    playlist_id = playlist['id']

    # 2. Add example tracks by BPM segments
    bpm_sections = {
        "flat": ["spotify:track:5HCyWlXZPP0y6Gqq8TgA20"],     # 160 bpm (e.g., Tame Impala)
        "uphill": ["spotify:track:4RVwu0g32PAqgUiJoXsdF8"],   # 140 bpm (e.g., Dua Lipa)
        "downhill": ["spotify:track:0VjIjW4GlUZAMYd2vXMi3b"]  # 170 bpm (e.g., The Weeknd)
    }

    tracks_to_add = bpm_sections['flat'] * 3 + bpm_sections['uphill'] * 2 + bpm_sections['downhill'] * 2

    requests.post(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
        json={"uris": tracks_to_add},
        headers=headers
    )

    return f"""
        <h3>✅ Playlist created!</h3>
        <p><a href="https://open.spotify.com/playlist/{playlist_id}" target="_blank">Open Playlist in Spotify</a></p>
    """


if __name__ == "__main__":
    app.run(debug=True)
