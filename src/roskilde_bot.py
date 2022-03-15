import argparse

from rich import print

import utils
from utils import (
    artists_top_tracks,
    get_artist_urls,
    get_uris_from_urls,
    loadCridentials,
    populate_playlist,
    setup_spotify_client,
    loadCridentials,
)
import os

playlist_uri = "09zoWGVW99ojUFnRnLmil4"


def fill_env_creds(args):
    valid_tokens = ["CLIENT_ID", "CLIENT_SECRET", "REDIRECT_URI", "PLAYLIST_URI"]
    creds = loadCridentials()

    for token in valid_tokens:
        if not getattr(args, token.lower()):
            if value := os.environ.get(token):
                setattr(args, token.lower(), value)
            elif value := creds.get(token):
                setattr(args, token.lower(), value)
    return args


def setup_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--client-id",
        help="Client id",
        type=str,
        nargs="?",
        default="",
        metavar="CLIENT-ID",
    )
    parser.add_argument(
        "-s",
        "--client-secret",
        help="Client secret",
        metavar="CLIENT-SECRET",
        type=str,
        nargs="?",
        default="",
    )
    parser.add_argument(
        "-r",
        "--redirect-uri",
        help="Redirect uri from spotify dashboard settings",
        metavar="REDIRECT-URI",
        type=str,
        nargs="?",
        default="",
    )
    parser.add_argument(
        "-p",
        "--playlist-uri",
        help="Playlist uri",
        metavar="PLAYLIST-URI",
        type=str,
        nargs="?",
        default="",
    )
    parser.add_argument(
        "-c",
        "--country",
        help="Country to get top tracks from",
        metavar="country",
        type=str,
        nargs="?",
        default="DK",
    )
    parser.add_argument(
        "-n",
        "--n-tracks",
        help="Number of maximum tracks for each artist",
        metavar="n-tracks",
        type=int,
        nargs="?",
        default=5,
    )

    args = parser.parse_args()
    args = fill_env_creds(args)

    return args


def main():
    args = setup_args()

    # Roskilde content section
    print(f"[bold cyan]Fetching artist uris from {utils.base_url}[/bold cyan]")
    artist_urls = get_artist_urls()
    artist_uris = get_uris_from_urls(artist_urls)

    # Spotify section
    print("[bold cyan]Fetching artist top tracks[/bold cyan]")
    spotify_client = setup_spotify_client(args)
    top_tracks = artists_top_tracks(
        artist_uris, spotify_client, country=args.country, max_tracks=args.n_tracks
    )

    print("[bold cyan]Adding tracks to playlist[/bold cyan]")
    populate_playlist(top_tracks, playlist_uri, spotify_client)


if __name__ == "__main__":
    main()
