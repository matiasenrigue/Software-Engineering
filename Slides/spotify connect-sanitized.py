import requests
import json
from pprint import pprint

###########BASIC

payload = {'key1': 'value1','key2': ['value2','value3']}
r = requests.get('http://httpbin.org/get', params=payload)
print(r.url)


##########CONNECTION

headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
}

URI = "https://api.spotify.com/v1/search"
r = requests.get(URI, params={'q':'bob','type':'artist','limit':2}, headers=headers)
pprint(json.loads(r.text))

##########MORE COMPLEX using SPOTIFY API

import sys
import spotipy
import spotipy.util as util

# Set the username and scope
username = "your_username"
scope = 'user-top-read'
client_id= 'your_client_id'
client_secret= 'your_client_secret'
redirect_uri= 'http://localhost:8888/callback'

# Generate the token
token = util.prompt_for_user_token(
    username=username,
    scope=scope,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri
)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    ranges = ['short_term','medium_term','long_term']

for range in ranges:
    print("range:", range)
    results = sp.current_user_top_tracks(time_range=range, limit=50)

    for i, item in enumerate(results['items']):
        print(i, item['name'], '//', item['artists'][0]['name'])
        print()
else:
    print("Can't get token for", username)