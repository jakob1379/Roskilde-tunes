from bs4 import BeautifulSoup
import progressbar as pbar
import re
import requests


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

if __name__ == '__main__':
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

    print("Finding their URI to use with api...")
    Pbar = pbar.ProgressBar()
    artistURIs = []
    for url in spotifyurls:
        uri = spotifyURL2URI(url)
        if uri is not None:
            artistURIs.append(uri)
    print(artistURIs)
