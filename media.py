import base64
from multiprocessing.pool import Pool

import requests
import os
import time
import six
import collections
from time import gmtime, strftime

import config_parser

SpotifyTracks = collections.namedtuple('SpotifyTracks', 'name id artist')

ac_token = ""

def get_sportify_playlist (playlist_name, config):
    print ("Retriving all titles form playlist")

    client_id = config.get('spotify', 'c_id')
    client_secret = config.get('spotify', 'c_secret')
    user_id = config.get('spotify', 'user_id')
    playlist_id = config.get('spotify', 'playlist_id')

    ac_tocken = get_ac_token(client_id, client_secret)

    get_track = "https://api.spotify.com/v1/users/"+ str(user_id)+"/playlists/"+ str(playlist_id)
    get_headers =  {'Authorization': 'Bearer ' + str(ac_tocken)}

    response = requests.get(get_track, headers=get_headers, verify=True)
    if response.status_code != 200:
        print ("Error getting the Playlist items")
        pass

    playlist_info = response.json()
    playlist_tracks = []
    for each_track in playlist_info['tracks']['items']:
        print (each_track['track']['name'])
        playlist_tracks.append(SpotifyTracks(id= each_track['track']['id'], name=each_track['track']['name'], artist= each_track['track']['artists']))
    return playlist_tracks


def get_youtube_id(sporify_track, api_key):
    search_String  = str(sporify_track.name) + " "
    for each_atrist in sporify_track.artist:
        search_String += str(each_atrist['name']) + " "

    payload = {'maxResults': '5', 'part':'snippet'}
    payload['key'] = api_key
    payload['q'] = str(search_String)
    youtube_url = "https://www.googleapis.com/youtube/v3/search"
    response = requests.get(youtube_url, params=payload)
    track_info = response.json()
    if(len(track_info['items']) > 1):
        track = track_info['items'][0]
        video_id = track['id']['videoId']
        return "https://www.youtube.com/watch?v="+ str(video_id)

def get_ac_token(client_id, client_secret):
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
    payload = {'grant_type': 'client_credentials'}
    payload['scope'] = "playlist-read-private"

    headers = _make_authorization_headers(client_id, client_secret)

    response = requests.post(OAUTH_TOKEN_URL, data=payload,
                             headers=headers, verify=True)
    if response.status_code != 200:
        pass
    token_info = response.json()
    ac_tocken = (token_info['access_token'])
    return ac_tocken


class SpotifyClientCredentials(object):
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id=None, client_secret=None, proxies=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_info = None
        self.proxies = proxies

    def get_access_token(self):
        if self.token_info and not self.is_token_expired(self.token_info):
            return self.token_info['access_token']

        token_info = self._request_access_token()
        token_info = self._add_custom_values_to_token_info(token_info)
        self.token_info = token_info

        return self.token_info['access_token']

    def _request_access_token(self):
        payload = { 'grant_type': 'client_credentials'}
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

def _make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(six.text_type(client_id + ':' + client_secret).encode('ascii'))
    return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}

def is_token_expired(token_info):
    now = int(time.time())
    return token_info['expires_at'] - now < 60

def move_files(music_dir):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    date  = strftime("%Y-%m-%d", gmtime())
    for filename in os.listdir(current_dir):
        if filename.endswith(".mp3"):
            new_file_name = filename.replace("  ", " ")
            new_file_name = filename.replace(' ' , '_')
            f_name = os.path.splitext(new_file_name)[0]
            new_name = music_dir + f_name + "_" + date + ".mp3"
            os.rename(current_dir +"/"+ filename, new_name)

def extract_mp3(command):
    os.system(command)


if __name__ == "__main__":

    config = config_parser.read_config()
    youtube_key = config.get('youtube', 'api_key')
    music_dir = config.get('media', 'music_dir')

    script_file = '/usr/bin/python ' +  os.path.dirname(os.path.realpath(__file__)) +'/mp3_extractor.py'

    all_tacks = get_sportify_playlist("test", config)
    commands = []
    for each_track in all_tacks:
        video_url = get_youtube_id(each_track, youtube_key)
        if (video_url is not None):
            command = script_file + ' ' + video_url
            commands.append(command)

    pool = Pool(8)
    results = pool.map(extract_mp3, commands)
    print ("all MP3's downloaded")
    move_files(music_dir)
