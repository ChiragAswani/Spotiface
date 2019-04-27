import requests
import json
import random


class Spotiface:
    def spotiface(self, access_token, device_id, data):
        face_api_url = 'https://eastus.api.cognitive.microsoft.com/face/v1.0/detect'
        params = {
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,' +
                                    'emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'
        };

        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': 'b5baf22e22a1473488798af89831ee10'
        }
        json_data = requests.post(face_api_url, params=params, headers=headers, data=data)
        pretty_json = json.loads(json_data.text)
        emotions = pretty_json[0]["faceAttributes"]['emotion']
        valence = self.calculate_valence(emotions)
        current_song = self.grab_song(access_token, 'classical', valence)
        print("Playing ", current_song["name"], " with valence as ", valence)
        self.play_song(access_token, device_id, current_song["uri"])

    def calculate_valence(self, emotions):
        neutral_factor = 0.5
        happiness = emotions['happiness'] / 2
        sadness = emotions['sadness'] / -2
        final_factor = neutral_factor + happiness + sadness
        return final_factor

    def grab_song(self, inputtoken, inputgenre, inputvalence):
        spotify_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + inputtoken,
        }
        spotify_params = (
            ('limit', '100'),
            ('market', 'ES'),
            ('seed_genres', inputgenre),
            ('target_valence', inputvalence),
        )
        response = requests.get('https://api.spotify.com/v1/recommendations', headers=spotify_headers,
                                params=spotify_params)
        pretty_json = json.loads(response.text)['tracks'][random.randint(0, 101)]
        return pretty_json

    def play_song(self, inputtoken, device_id, track_uri):
        spotify_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + inputtoken,
        }
        spotify_params = (
            ('device_id', device_id),
        )
        data = '{"uris":[' + '"' + track_uri + '"' + '],"position_ms":0}'
        requests.put('https://api.spotify.com/v1/me/player/play', headers=spotify_headers, params=spotify_params,
                     data=data)
