import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load API keys
load_dotenv()
TM_API_KEY = os.getenv("TICKETMASTER_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "http://localhost:8080"

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-modify-public"
))

# Enter User-Specific Information
USER_ID = "nial.tilson"
PLAYLIST_NAME = "Upcoming Concerts in PDX"

def get_concerts(city="Portland", country_code="US"):
    """Fetch concerts from Ticketmaster API"""
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={TM_API_KEY}&city={city}&countryCode={country_code}&classificationName=music"
    response = requests.get(url).json()
    
    artists = set()
    if "_embedded" in response:
        for event in response["_embedded"]["events"]:
            for attraction in event["_embedded"]["attractions"]:
                artists.add(attraction["name"])
    return list(artists)

def create_or_get_playlist():
    """Create or find an existing Spotify playlist"""
    playlists = sp.user_playlists(USER_ID)
    for playlist in playlists["items"]:
        if playlist["name"] == PLAYLIST_NAME:
            return playlist["id"]
    
    new_playlist = sp.user_playlist_create(USER_ID, PLAYLIST_NAME, public=True)
    return new_playlist["id"]

def search_and_add_songs(artists, playlist_id):
    """Find artists on Spotify and add their top songs"""
    track_uris = []
    for artist in artists:
        result = sp.search(q=artist, type="artist", limit=1)
        if result["artists"]["items"]:
            artist_id = result["artists"]["items"][0]["id"]
            top_tracks = sp.artist_top_tracks(artist_id, country="US")
            if top_tracks["tracks"]:
                track_uris.append(top_tracks["tracks"][0]["uri"])
                
    if track_uris:
        sp.playlist_replace_items(playlist_id, track_uris)

def main():
    artists = get_concerts()
    if not artists:
        print("No concerts found.")
        return
    
    playlist_id = create_or_get_playlist()
    search_and_add_songs(artists, playlist_id)
    print("Playlist updated!")

if __name__ == "__main__":
    main()
