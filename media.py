from multiprocessing.pool import Pool
import requests
import os
import collections
from time import gmtime, strftime
import config_parser
from spotify_client import SpotifyClient, SpotifyOAuthClient

AccessKey = collections.namedtuple('AccessKey', 'key expires_at')

ac_token = ""

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

# def get_ac_token(client_id, client_secret):
#     OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
#     payload = {'grant_type': 'client_credentials'}
#     payload['scope'] = "playlist-read-private"
#
#     headers = _make_authorization_headers(client_id, client_secret)
#
#     response = requests.post(OAUTH_TOKEN_URL, data=payload,
#                              headers=headers, verify=True)
#     if response.status_code != 200:
#         pass
#     token_info = response.json()
#     ac_tocken = (token_info['access_token'])
#     return ac_tocken



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
    print ("test")
    config = config_parser.read_config()
    test = SpotifyOAuthClient(config)
    token = test.get_auth_token()
    test.get_tokens()
    if token:
        test.del_playlist_tracks(token)
        sportiy = SpotifyClient(config)
        tracks = sportiy.del_playlist_tracks()

        print (tracks)
    # config = config_parser.read_config()
    # youtube_key = config.get('youtube', 'api_key')
    # music_dir = config.get('media', 'music_dir')

    # script_file = '/usr/bin/python ' +  os.path.dirname(os.path.realpath(__file__)) +'/mp3_extractor.py'

    # all_tacks = get_sportify_playlist("test", config)
    # commands = []
    # for each_track in all_tacks:
    #     video_url = get_youtube_id(each_track, youtube_key)
    #     if (video_url is not None):
    #         command = script_file + ' ' + video_url
    #         commands.append(command)

    # pool = Pool(8)
    # results = pool.map(extract_mp3, commands)
    # print ("all MP3's downloaded")
    # move_files(music_dir)