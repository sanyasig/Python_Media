import requests
import time
import six
import collections
import base64
import json
import six
import six.moves.urllib.parse as urllibparse

def _make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(six.text_type(client_id + ':' + client_secret).encode('ascii'))
    return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}

def is_token_expired(token_info):
    now = int(time.time())
    return token_info['expires_at'] - now < 60

SpotifyTracks = collections.namedtuple('SpotifyTracks', 'name id artist')


class SpotifyOAuthClient(object):
    def __init__(self, config):
        self.client_id = config.get('spotify', 'c_id')
        self.client_secret = config.get('spotify', 'c_secret')
        self.user_id = config.get('spotify', 'user_id')
        self.playlist_id = config.get('spotify', 'playlist_id')
        self.token_info = None
        self.proxies = None
        self.config = config
        self.access_token = None

    def get_auth_token(self):

        if self.config.get('spotify', 'auth_code'):
            self.access_token = self.config.get('spotify', 'auth_code')
            return self.access_token
        else:
            OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
            payload = {'client_id': self.client_id, 'response_type': 'code', 'redirect_uri': 'https://localhosts.com/',
                       'scope': "playlist-modify-private"}

            urlparams = urllibparse.urlencode(payload)
            print("%s?%s" % (OAUTH_AUTHORIZE_URL, urlparams))

    def del_playlist_tracks(self, token):
        get_track = "https://api.spotify.com/v1/users/" + str(self.user_id) + "/playlists/" + str(self.playlist_id)
        get_headers = {'Authorization': 'Bearer ' + str(token)}
        response = requests.get(get_track, headers=get_headers, verify=True)
        if response.status_code != 200:
            print ("Error getting the Playlist items")
            pass
        playlist_info = response.json()
        playlist_tracks = []

        for each_track in playlist_info['tracks']['items']:
            track_uri = each_track['track']['uri']
            del_track = {'uri': str(each_track['track']['uri'])}
            playlist_tracks.append(del_track)
        test = {}
        test['tracks'] = playlist_tracks
        del_payload = json.dumps(test, ensure_ascii=False)

        del_pt_url = get_track + "/tracks"

        response = requests.delete(del_pt_url, data=del_payload, headers=get_headers)

        if response.status_code != 200:
            print ("Error Deleting tracks from playlist")
            pass

        print del_payload


    def get_tokens(self):
        OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
        try:
            response = raw_input("Enter the URL you were redirected to: ")
        except NameError:
            response = input("Enter the URL you were redirected to: ")

        print()
        print()

        authorize_code = response.split("?code=")[1].split("&")[0]
        payload = {'redirect_uri': self.redirect_uri,
                   'code': authorize_code,
                   'grant_type': 'authorization_code'}
        headers = _make_authorization_headers(self.client_id, self.client_secret)

        response = requests.post(OAUTH_TOKEN_URL, data=payload,
            headers=headers, verify=True, proxies=self.proxies)
        if response.status_code != 200:
            pass
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        self._save_token_info(token_info)

class SpotifyClient(object):
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, config):
        self.client_id = config.get('spotify', 'c_id')
        self.client_secret = config.get('spotify', 'c_secret')
        self.user_id = config.get('spotify', 'user_id')
        self.playlist_id = config.get('spotify', 'playlist_id')
        self.token_info = None
        self.proxies= None

    def get_access_token(self):
        if self.token_info and not self.is_token_expired(self.token_info):
            return self.token_info['access_token']

        token_info = self._request_access_token()
        token_info = self._add_custom_values_to_token_info(token_info)
        self.token_info = token_info
        return self.token_info['access_token']

    def _request_access_token(self):
        payload = { 'grant_type': 'client_credentials'}
        payload['scope'] = "playlist-modify-private"
        headers = _make_authorization_headers(self.client_id, self.client_secret)
        response = requests.post(self.OAUTH_TOKEN_URL, data=payload,
            headers=headers, verify=True, proxies=self.proxies)
        if response.status_code != 200:
          pass
        token_info = response.json()
        return token_info

    def is_token_expired(self, token_info):
        return is_token_expired(token_info)

    def _add_custom_values_to_token_info(self, token_info):
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
        return token_info

    def get_sportify_playlist(self, playlist_name):
        get_track = "https://api.spotify.com/v1/users/" + str(self.user_id) + "/playlists/" + str(self.playlist_id)
        get_headers = {'Authorization': 'Bearer ' + str(self.get_access_token())}
        response = requests.get(get_track, headers=get_headers, verify=True)
        if response.status_code != 200:
            print ("Error getting the Playlist items")
            pass
        playlist_info = response.json()
        playlist_tracks = []
        for each_track in playlist_info['tracks']['items']:
            print (each_track['track']['name'])
            playlist_tracks.append(SpotifyTracks(id=each_track['track']['id'], name=each_track['track']['name'],
                                                 artist=each_track['track']['artists']))
        return playlist_tracks

    def del_playlist_tracks(self):
        get_track = "https://api.spotify.com/v1/users/" + str(self.user_id) + "/playlists/" + str(self.playlist_id)
        get_headers = {'Authorization': 'Bearer ' + str(self.get_access_token())}
        response = requests.get(get_track, headers=get_headers, verify=True)
        if response.status_code != 200:
            print ("Error getting the Playlist items")
            pass
        playlist_info = response.json()
        playlist_tracks = []

        for each_track in playlist_info['tracks']['items']:
            track_uri = each_track['track']['uri']
            del_track = {'uri': str(each_track['track']['uri'])}
            playlist_tracks.append(del_track)
        test = {}
        test['tracks'] = playlist_tracks
        del_payload = json.dumps(test, ensure_ascii=False)

        del_pt_url =  get_track + "/tracks"

        response = requests.delete(del_pt_url, data=del_payload, headers=get_headers)

        if response.status_code != 200:
            print ("Error Deleting tracks from playlist")
            pass

        print del_payload