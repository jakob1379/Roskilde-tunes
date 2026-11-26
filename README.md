# Roskilde tunes

<p align="center">
  <img src=".github/assets/lineup-to-playlist.svg" width="100%" alt="Diagram of the pipeline: acts leave the Roskilde Festival line-up page, each act page's Spotify embed gives an artist id, that artist's top tracks are sorted by popularity and the top five kept, and those tracks fill your Spotify playlist.">
</p>

A Python script that turns the Roskilde Festival 2022 line-up into a Spotify
playlist of each announced artist's top tracks.

## How it works

1. Reads the line-up at `roskilde-festival.dk/da/line-up/` and collects every
   link to a 2022 act page.
2. Opens each act page and pulls the Spotify artist id out of its embedded
   Spotify player.
3. Asks Spotify for each artist's top tracks in a country (default `DK`),
   sorts them by popularity and keeps the first `n` (default 5).
4. Empties your playlist, then adds all collected tracks to it.

> [!WARNING]
> Step 4 replaces everything already in the playlist. Point it at a playlist
> you made for this.

## Setup

You need Python 3.8 or newer and an app on the
[Spotify developer dashboard](https://developer.spotify.com/dashboard/applications),
which gives you a client id, client secret and redirect URI.

```bash
git clone https://github.com/jakob1379/Roskilde-tunes.git
cd Roskilde-tunes
pip install -r requirements.txt
```

### Credentials

Each value can come from a command-line flag, an environment variable, or a
`creds.json` file in the directory you run the script from (`src`). A flag wins
over the environment variable, which wins over the file.

| Value          | Flag                   | Environment variable / `creds.json` key |
| -------------- | ---------------------- | --------------------------------------- |
| Client id      | `-i`, `--client-id`     | `CLIENT_ID`                             |
| Client secret  | `-s`, `--client-secret` | `CLIENT_SECRET`                         |
| Redirect URI   | `-r`, `--redirect-uri`  | `REDIRECT_URI`                          |
| Playlist URI   | `-p`, `--playlist-uri`  | `PLAYLIST_URI`                          |

An example `src/creds.json`:

```json
{
    "CLIENT_ID": "<client_id>",
    "CLIENT_SECRET": "<client_secret>",
    "REDIRECT_URI": "https://localhost:8080",
    "PLAYLIST_URI": "<playlist_uri>"
}
```

The redirect URI must match one set in your Spotify app's settings. The script
asks for the `playlist-modify-public` scope, so use a public playlist.

## Usage

```bash
cd src
export PLAYLIST_URI="<playlist_uri>"
python roskilde_bot.py
```

On the first run Spotify asks you to log in and approve the app. Options:

```console
$ python roskilde_bot.py -h
usage: roskilde_bot.py [-h] [-i [CLIENT-ID]] [-s [CLIENT-SECRET]]
                       [-r [REDIRECT-URI]] [-p [PLAYLIST-URI]] [-c [country]]
                       [-n [n-tracks]] [-q]

options:
  -h, --help            show this help message and exit
  -i, --client-id [CLIENT-ID]
                        Client id
  -s, --client-secret [CLIENT-SECRET]
                        Client secret
  -r, --redirect-uri [REDIRECT-URI]
                        Redirect uri from spotify dashboard settings
  -p, --playlist-uri [PLAYLIST-URI]
                        Playlist uri
  -c, --country [country]
                        Country to get top tracks from
  -n, --n-tracks [n-tracks]
                        Number of maximum tracks for each artist
  -q, --quiet           do not produce print anything
```

## Development

Versions follow Conventional Commits via Commitizen. `./update_version` bumps
the version and regenerates [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE.md). Written by Jakob Guldberg Aaes.
