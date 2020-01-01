from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials
import progressbar as pbar
import re
import requests
import spotipy
import spotipy.util as util

def artistURL():
    url = 'https://www.roskilde-festival.dk/en/line-up/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    a_tags = soup.findAll('a', {"class":"name"})
    return ['https://www.roskilde-festival.dk' + tag.attrs['href']
           for tag in a_tags]


def artist2spotifyURL(weburl):
    response = requests.get(weburl)
    soup = BeautifulSoup(response.text, "html.parser")
    tags = soup.findAll('iframe', {'class':'SpotifyPlayer'})
    for elem in tags:
        return elem.attrs['src']
    return None


def spotifyURL2URI(test_str):
    regex = r"([A-Za-z0-9]+)\?si"

    matches = re.finditer(regex, test_str, re.MULTILINE)
    for _, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            return match.group(groupNum)

    return None

def extractSpotifyURI():
    print("Extracting artist urls...")
    artisturls = artistURL()

    print("Searching for their spotify urls...")
    spotifyurls = []
    Pbar = pbar.ProgressBar()
    for url in Pbar(artisturls):
        spoturl = artist2spotifyURL(url)
        if spoturl is not None:
            spotifyurls.append(spoturl)
    print(f"Found {len(spotifyurls)} artists with links to spotify")

    print("Searching for their URI to use with api...")
    Pbar = pbar.ProgressBar()
    artistURIs = []
    for url in spotifyurls:
        uri = spotifyURL2URI(url)
        if uri is not None:
            artistURIs.append(uri)
    return artistURIs


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


def tracksFromPlayList(spotifyClient, username, playlist): #
    results = spotifyClient.user_playlist(username, playlist_id=playlist)

    results = spotifyClient.user_playlist_tracks(username, playlist)
    tracks = results['items']
    while results['next']:
        results = spotifyClient.next(results)
        tracks.extend(results['items'])

    return [track['track']['uri'] for track in tracks]


def loadTrackURIs(spotifyClient, uris=[], load=False, save=True):
    tracks = []
    if load:
        print("loading previous saved songs...")
        with open('tracks.txt', 'r') as f:
            for line in f:
                tracks.append(line.strip())
    else:
        print("finding artists top songs...")
        Pbar = pbar.ProgressBar()
        for uri in Pbar(uris):
            tracks += findArtistsTopN(spotifyClient, uri)

        if save:
            with open('tracks.txt', 'w+') as f:
                for track in tracks:
                    f.write(track + '\n')
    return tracks

def removeDuplicates(spotify, uris, user, playlist):
    Pbar = pbar.ProgressBar()
    tracks = [spotify.track(uri) for uri in Pbar(uris)]

    for k, v in tracks[0].items():
        if k not in ['album', 'available_markets', 'preview_url', 'explicit',
                     'disc_number']:
            print(f"{k+':':20}", v)


    for i, track in enumerate(tracks):

        otherTracks = tracks.copy()
        otherTracks.pop(i)

        for t in otherTracks:
            # check names
            if track['name'] in t['name']:
                # check artists
                otherArtists = [artist['name'] for artist in t['artists']]
                if any([artist['name'] in otherArtists
                        for artist in track['artists']]):
                    print()
                    print("duplicate name found for:")
                    print('[1] ', track['name'])
                    print("by ",
                          [artist['name'] for artist in track['artists']])
                    print("Matched by: ")
                    print('[2] ', t['name'])
                    print("by ",
                          [artist['name'] for artist in t['artists']])
                    print()
                    ans = int(
                        input("Which one [1/2] - 0 for none: ").strip()) - 1
                    if ans == -1:
                        pass
                    elif ans == 0:
                        spotify.user_playlist_remove_all_occurrences_of_tracks(
                            user, playlist, [track['id']])
                        tracks.remove(track)
                    elif ans == 1:
                        spotify.user_playlist_remove_all_occurrences_of_tracks(
                            user, playlist, [t['id']])
                        tracks.remove(t)

    uris = [track['uri'] for track in tracks]
    return uris
