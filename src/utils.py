import json
import re
from itertools import chain

import requests
import spotipy
from bs4 import BeautifulSoup
from rich.progress import track
from spotipy.oauth2 import SpotifyOAuth
from wrapt_timeout_decorator import timeout

# urls
base_url = "https://www.roskilde-festival.dk"

# TimeOuts
max_artist_time = 20
max_uri_time = 120
max_top_track_time = 120


@timeout(max_artist_time)
def get_artist_urls():
    lineup_url = base_url + "/da/line-up/"
    lineup_content = requests.get(lineup_url).content
    soup = BeautifulSoup(lineup_content, features="html.parser")

    artist_tags = soup.find_all("a", href=re.compile(r"/da/years/2022/acts/"))
    artist_urls = [
        artist_tag.attrs["href"]
        for artist_tag in artist_tags
        if "href" in artist_tag.attrs
    ]

    return artist_urls


@timeout(max_uri_time)
def get_uris_from_urls(artist_urls):
    uri_from_url = re.compile(r"\/artist\/([a-zA-Z0-9]+)+\?si=")
    spotify_uris = []

    for artist_url in track(artist_urls):
        artist_content = requests.get(base_url + artist_url).content
        soup = BeautifulSoup(artist_content, features="html.parser")

        iframes = soup.find_all(
            "iframe", {"data-src": re.compile(r"open\.spotify\.com")}
        )

        spotify_uris.extend(
            chain(
                *[
                    uri_from_url.findall(frame.attrs["data-src"])
                    for frame in iframes
                    if "data-src" in frame.attrs
                ]
            )
        )

    return spotify_uris


def loadCridentials():
    with open("creds.json", "rb") as f:
        creds = json.load(f)
    return creds


def setup_spotify_client():
    creds = loadCridentials()

    # Timeouts
    max_artist_time = 10  # seconds
    max_uri_time = 60

    # Spotify Client
    scope = ["playlist-modify-public"]

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            redirect_uri=creds["redirect_uri"],
        )
    )
    return sp


@timeout(max_top_track_time)
def artists_top_tracks(artist_uris, client, country="DK", max_tracks=5):
    all_tracks = []
    for artist_uri in track(artist_uris):
        tracks = client.artist_top_tracks(artist_uri, country=country)["tracks"]
        tracks.sort(key=lambda track: track["popularity"], reverse=True)
        track_uris = [track["uri"].split(":")[-1] for track in tracks]
        all_tracks.extend(track_uris[:max_tracks])
    return all_tracks


def populate_playlist(tracks, playlist_uri, client):
    client.playlist_replace_items(playlist_uri, [])
    for i in range(0, len(tracks), 100):
        client.playlist_add_items(playlist_uri, tracks[i : i + 100])
