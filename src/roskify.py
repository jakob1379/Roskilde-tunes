# -*- coding: utf-8 -*-
from roskifyutils import \
    extractSpotifyURI, \
    findArtistsTopN, \
    listPlaylists, \
    loadArtistURI, \
    loadTrackURIs, \
    removeDuplicates, \
    setupSpotifyClient, \
    tracksFromPlayList
import argparse
import progressbar as pbar
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--user-id",
                    help="Provide your user id which can be optained by " +
                    "going to https://open.spotify.com/ and vieweing "+
                    "your profile",
                    type=str,
                    nargs='?',
                    default='1130349271')
parser.add_argument("-p", "--playlist",
                    help="id of the playlist to operate on",
                    type=str,
                    nargs='?',
                    default='1L7qcjzDKSdtXNZuhztl2z')
parser.add_argument("-l", "--list-playlists",
                    help="if a user id is provided, list their playlists",
                    action='store_true')
parser.add_argument("-r", "--read-old-songs",
                    help="Don't fetch songs anew, but read from last run " +
                    "instead.",
                    action='store_true')

args = parser.parse_args()

USERID = args.user_id      #
PLAYLIST = args.playlist

if __name__ == '__main__':
    print("Setting up spotify api parser...")
    sp = setupSpotifyClient(username=USERID)
    userid = sp.client_credentials_manager.client_id
    if args.list_playlists:
        listPlaylists(sp, USERID)
        sys.exit()


    print("extracting tracks from URIs...")
    uris = extractSpotifyURI()
    tracksOnPlayList = tracksFromPlayList(sp, USERID, PLAYLIST)
    tracks = loadTrackURIs(sp, uris, load=args.read_old_songs)
    print(f"Removing duplicates...")
    tracks = removeDuplicates(sp, list(set(tracks+tracksOnPlayList)),
                              USERID, PLAYLIST)

    # only add the tracks that are not already on the PLAYLIST
    print(f"Tracks found: {len(tracks)}")
    print(f"Tracks on playlist: {len(tracksOnPlayList)}")
    tracks = list(set(tracks) - set(tracksOnPlayList))

    if len(tracks) == 0:
        print("No new tracks to add.")
        sys.exit()

    print(f"Tracks with ids not on playlist: {len(tracks)}")
    ans = input("Should the missing tracks be added? [y/N] ")

    if ans.lower() == 'y':
        print("adding songs to playlist...")
        Bar = pbar.ProgressBar()
        for track in Bar(tracks):
            sp.user_playlist_add_tracks(userid,
                                        playlist_id=PLAYLIST,
                                        tracks=[track])
