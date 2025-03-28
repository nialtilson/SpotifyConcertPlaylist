# SpotifyConcertPlaylist
A Playlist to scrub local concert venues (or ticket sales) for coming artists and their songs to sample


1. Install Required Packages

First, open Terminal and install the necessary Python libraries:

pip install requests spotipy python-dotenv

    requests → Fetch concert data from Ticketmaster API

    spotipy → Manage Spotify playlists

    python-dotenv → Store API keys securely

2. Get Your API Keys

You'll need API keys from:

    Ticketmaster → Get API Key

    Spotify → Get API Key

Store them in a .env file in the same directory as your script:

TICKETMASTER_API_KEY=your_ticketmaster_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

3. Create the Python Script

Save the following script as update_concert_playlist.py:

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

USER_ID = "your_spotify_user_id"
PLAYLIST_NAME = "Upcoming Concerts in Town"

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

4. Make the Script Executable

In Terminal, navigate to the script's folder and run:

chmod +x update_concert_playlist.py

5. Automate with launchd (MacOS equivalent of Cron Jobs)

    Open Terminal and type:

mkdir -p ~/Library/LaunchAgents

Create a .plist file to schedule the script:

nano ~/Library/LaunchAgents/com.user.concertplaylist.plist

Add the following XML code:

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.user.concertplaylist</string>
        
        <key>ProgramArguments</key>
        <array>
            <string>/usr/bin/python3</string>
            <string>/path/to/update_concert_playlist.py</string>
        </array>

        <key>StartCalendarInterval</key>
        <dict>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>

        <key>RunAtLoad</key>
        <true/>
    </dict>
</plist>

Save & Exit (Press CTRL + X, then Y, then Enter).

Load the job:

    launchctl load ~/Library/LaunchAgents/com.user.concertplaylist.plist

That's it! 🎵 Your Mac will now run the script daily at 9 AM to update your playlist with artists performing in your city. 🚀