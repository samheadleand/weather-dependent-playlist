#!/usr/bin/python3
import json
import pprint
import urllib.request
import iso8601
from datetime import date
from datetime import datetime
import sys
import os
import subprocess
import time
import spotipy
import spotipy.util as util


def get_forecast_url():
    """Load forecast data from a MetOffice datapoint API

    This is provided from the MetOffice API is in JSON format. The file requested
    is for the Manchester forecast. The API returns a dictionary with one entry
    of SiteRep so the file returned only brings back the dictionary within SitRep.

    :returns: structured data from the file in datapoint API format
    :rtype: dict
    """
    with urllib.request.urlopen('http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/310013?res=3hourly&key=b2651cbf-8081-437b-82e9-d71f7a3bf5cb') as response:
        return json.loads(response.read().decode())['SiteRep']

#print(get_forecast_url())	

def tidy_weird_date_format(weird_date):
    """Converts date format of form '2018-01-01Z' to '2018-01-01'

    MetOffice API returns dates with a Z on the end to represent the fact it's
    UTC. This is not recognised by libraries so we convert it by taking off the
    Z. The input is only part validated, some bad inputs will result in bad
    outputs.

    :param str weird_date: date of the form '2018-01-01Z'
    :returns: date of the form '2018-01-01'
    :rtype: str
    :raises ValueError: on part validation failure
    """
    if weird_date[-1] == 'Z':
        return weird_date[:-1]
    else:
        raise ValueError('Wrong date format provided')

def get_days_forecast():
    forecast = get_forecast_url()
    list_of_forecasts = forecast['DV']['Location']['Period']
    check_date = datetime.combine(date.today(), datetime.min.time())
    check_forecast = []
    for day in list_of_forecasts:
        forecast_date = tidy_weird_date_format(day['value'])
        if iso8601.parse_date(forecast_date).replace(tzinfo=None) == check_date:
            check_forecast = day
            break
    return check_forecast

#print(type(get_days_forecast()))

def get_next_3_hours_forecast():
    todays_forecast = get_days_forecast()
    next_3_hour = todays_forecast['Rep'][0]
    return int(next_3_hour['W'])

print(get_next_3_hours_forecast())

def categorize_weather(weather_number):
    if weather_number in [1,3]:
        return 'Sunny'
    elif weather_number in [5,6,7,8]:
        return 'Overcast'
    elif weather_number in [16,17,18,19,20,21,22,23,24,25,26,27]:
        return 'Snowy'
    elif weather_number in [13,14,15,28,29,30]:
        return 'Rainy'
    elif weather_number in [9,10,11,12]:
        return 'Drizzle'
    elif weather_number in [0,2]:
        return 'Clear Night'
    else:
        return 'Unknown'

#print(categorize_weather(8))
#print(categorize_weather(get_next_3_hours_forecast()))

# Creates a playlist for a user

username = 'samheadleand'
playlist_name = 'weather_playlist'+ str(date.today())
print(playlist_name)
"""
playlist_description = ''
#SPOTIPY_CLIENT_ID='c18c86887bfd445bbff29a8bc1e000f9'
#SPOTIPY_CLIENT_SECRET='a6971a033cd34801a4e21bb0b9baecdf'
SPOTIPY_REDIRECT_URI='http://localhost/'
my_scope='playlist-modify-public'
token = util.prompt_for_user_token(username,scope=my_scope, redirect_uri=SPOTIPY_REDIRECT_URI)

sp = spotipy.Spotify(auth=token)


# Try to add playlist


def create_playlist_and_return_id(playlist_name, create=True):
    if create:
        sp.user_playlist_create(username, name=playlist_name,public=True)

    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            return playlist['id']


def find_song_with_name_like(list_of_search_terms):
    songs = []
    song_name = []
    for name in list_of_search_terms:
        results = sp.search(q='track:'+name, limit=30)
        items = results['tracks']['items']
        for idx in items:
            name = idx['name']
            if name in song_name:
                pass
            else:
                song_name.append(name)
                songs.append(idx['uri'])
    return songs


#Find Artist

def find_artists_with_name_like(list_of_words):
    artists = []
    artist_name = []
    for name in boat_names:
        results = sp.search(q='artist:' + name, type='artist', limit=10)
        items = results['artists']['items']

        for idx in items:
            name = idx['name']
            if name in artist_name:
                pass
            else:
                artist_name.append(name)
                artists.append(idx['uri'])
    return artists


def find_top_x_songs_by_artist(list_of_artist_uri, top_n_tracks):
    songs = []
    for idx in list_of_artist_uri:
        results = sp.artist_top_tracks(idx)
        for track in results['tracks'][:top_n_tracks]:
            songs.append(track['id'])
    return songs

def remove_songs_with_low_pop_from_list(list_of_track_ids, minimum_pop_score):
    new_songs = []
    for song in list_of_track_ids:
        if sp.track(song)['popularity'] >= minimum_pop_score:
            new_songs.append(song)
    return new_songs


def add_songs_to_playlist(playlist_id, list_of_song_uri, username='samheadleand'):
    for song in list_of_song_uri:
        sp.user_playlist_add_tracks(username, playlist_id, [song])
        time.sleep(2)
#print(new_songs)



playlist_name = 'Boats boats boats'
boat_names = ['Canal','Boat', 'Water', 'River', ]
other_boat_names=['Barge', 'Lock', 'Rudder', 'Duck', 'Sea']
other_boat_names2=['Sluice', 'Sail', 'Water', 'Ocean', 'Knot', 'Anchor']
false_playlist = [boat_names, other_boat_names, other_boat_names2]

playlists = []
for plist in false_playlist:
    for word in plist:
        playlists.append([word])
print(playlists)

playlist_id = create_playlist_and_return_id('Boats boats boats')

song_in_list = []

for idx in playlists:
    print(idx)
    print(len(song_in_list))
    artists = find_artists_with_name_like(idx)
    songs = find_top_x_songs_by_artist(artists, 10)
    new_songs = remove_songs_with_low_pop_from_list(songs, 50)
    songs_to_be_added = []
    for song in new_songs:
        if song not in song_in_list:
            song_in_list.append(song)
            songs_to_be_added.append(song)
    add_songs_to_playlist(playlist_id, songs_to_be_added)

    songs = find_song_with_name_like(idx)
    new_songs = remove_songs_with_low_pop_from_list(songs, 50)
    for song in new_songs:
        if song not in song_in_list:
            song_in_list.append(song)
            songs_to_be_added.append(song)
    add_songs_to_playlist(playlist_id, songs_to_be_added)


"""
