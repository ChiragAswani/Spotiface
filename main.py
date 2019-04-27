from flask import Flask, render_template, Response, request
from camera import VideoCamera
from urllib.parse import quote
import requests
import json

app = Flask(__name__)

#  Client Keys
CLIENT_ID = "9ed7f0f79e6e43b3975bcb6653c3a5bc"
CLIENT_SECRET = "2459cc3403e44f8e9c4a51fe6cec498d"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://0.0.0.0"
PORT = 5000
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-read-playback-state user-modify-playback-state"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route('/')
def index():
	url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
	auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
	return render_template('index.html', auth_url=auth_url, active_device="INIT")

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    device_id = request.args['device_id']
    access_token = request.args['access_token']
    return Response(gen(VideoCamera(device_id, access_token)),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get profile data
    user_devices_endpoint = "https://api.spotify.com/v1/me/player/devices"
    user_devices_response = requests.get(user_devices_endpoint, headers=authorization_header)
    user_devices = json.loads(user_devices_response.text)
    for device in user_devices["devices"]:
        if device["is_active"]:
            return render_template("index.html", active_device=device, access_token=access_token)
    return render_template("index.html", active_device="NONE")
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)