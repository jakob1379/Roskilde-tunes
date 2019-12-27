from spotipy.oauth2 import SpotifyClientCredentials
import spotify.sync as spotify
import spotipy
import spotipy.util as util
import progressbar as pbar

def findArtistsTopN(spotifyClient, artistURI, n=5, v=False):
    trackURIS = []
    # Get artist name and id
    result = spotifyClient.artist(artistURI)
    name = result['name']
    sID = result['id']
    if v:
        print(name, sID)

    # find top tracks for artist
    result = spotifyClient.artist_top_tracks(sID)
    for track in result['tracks'][:n]:
        if v:
            print('track    : ' + track['name'] +'\nURI      :   '
                  + track['uri'])
        trackURIS.append(track['uri'])
    if v:
        print()
    return trackURIS

def loadArtistURI():
    output = []
    with open("data/artistURI.txt") as f:
        for line in f:
            output.append(line.strip())
    return output

def loadCridentials():
    with open("cridentials/ClientID") as f:
        cID = f.read().replace('\n', '')
    with open("cridentials/ClientSecret") as f:
        cSecret = f.read().replace('\n', '')
    return cID, cSecret

def setupSpotifyClient(username='jakob1379'):
    client_id, client_secret = loadCridentials()
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret)

    token = util.prompt_for_user_token(username,
                                       scope='playlist-modify-public',
                                       client_id=client_id,
                                       client_secret=client_secret,
                                       redirect_uri='https://localhost:8080')
    return spotipy.Spotify(
        client_credentials_manager=client_credentials_manager,
        auth=token)


def show_tracks(tracks):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i, track['artists'][0]['name'],
                                    track['name']))

def listPlaylists(spotifyClient, username):
    playlists = spotifyClient.user_playlists(username)
    print()
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            print()
            print(playlist['name'], playlist['id'])
            print('  total tracks', playlist['tracks']['total'])


def tracksFromPlayList(spotifyCleint, username, playlist):
    result = spotifyCleint.user_playlist(username, playlist_id=playlist)
    return [elem['track']['uri'] for elem in result['tracks']['items']]


def loadTrackURIs(spotifyClient, uris=[], load=False, save=True):
    tracks = []
    if load:
        with open('data/tracks.txt') as f:
            for line in f:
                tracks.append(line.strip())
    else:
        Pbar = pbar.ProgressBar()
        for uri in Pbar(uris):
            tracks += findArtistsTopN(spotifyClient, uri)

        if save:
            with open('data/tracks.txt', 'w') as f:
                for track in tracks:
                    f.write(track + '\n')
    return tracks
