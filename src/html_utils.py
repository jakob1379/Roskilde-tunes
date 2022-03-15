import re
from itertools import chain

import requests
from bs4 import BeautifulSoup
from rich.progress import track
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
