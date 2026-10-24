#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["ytmusicapi>=1.10"]
# ///
"""
List the unique albums in a public YouTube Music playlist, in playlist order.

For each album you get: artist, album title, release date, genre, type
(Album/EP/Single), album art URL, and the YouTube Music album link.

Where the data comes from:
  - YouTube Music (via ytmusicapi, no login needed): playlist tracks, album
    artist/title/type, year, album art, album link.
  - iTunes Search API: release date (the official street date).
  - MusicBrainz: genres (e.g. "atmospheric black metal"), plus the release
    date when iTunes doesn't have the album.
  - If MusicBrainz has no genres, iTunes' genre is used. It is broad ("Metal").
  A date is only used if its year agrees with YouTube Music's year. If neither
  site finds the album, the date is just that year and the genre is blank.

Usage:
  uv run gather_youtube_music_albums.py "https://music.youtube.com/playlist?list=..."
  uv run gather_youtube_music_albums.py URL [URL ...] --format csv -o october.csv
  uv run gather_youtube_music_albums.py            # prompts for a URL
  uv run gather_youtube_music_albums.py URL \
      --download-art site/content/images/2027-02-01-my-favorite-records-of-2026

  With plain python3, install the dependency first: pip install ytmusicapi

Output formats (--format):
  text  readable list with full release dates and art URLs (default)
  csv   rows for the "Music Listening" Google Sheet, same columns and order:
        Band, Album Title, Spotify, Youtube Music, Bandcamp, Referred by,
        Genre, Notes, Score (out of 10), Release Date
        Release Date is the month (2026-01), like the sheet. Spotify, Bandcamp,
        Referred by, Notes and Score are left blank for you to fill in.
        There's no header row, so the file can be appended to the sheet
        (File > Import > Upload > "Append to current sheet"). Add --header
        to include one.
  tsv   same as csv but tab separated, for pasting straight into the sheet

Progress and warnings go to stderr, so `> file.csv` captures only the data.

--download-art DIR saves each album's art into DIR named like past posts'
images: "Florence + The Machine" -> FlorenceAndTheMachine.jpg. A band with more
than one album in the list gets the album name too (UltharHelionomicon.jpg).
Files that already exist are left alone.
"""

import argparse
import csv
import difflib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

try:
    from ytmusicapi import YTMusic
except ImportError:
    sys.exit(
        "Missing dependency ytmusicapi. Either run with `uv run "
        "gather_youtube_music_albums.py ...` or `pip install ytmusicapi`."
    )

# MusicBrainz asks API clients to identify themselves.
USER_AGENT = "karlgrz.com-album-gatherer/1.0 ( https://karlgrz.com )"
MAX_GENRES = 3

# Columns of the "Music Listening - YYYY" Google Sheet, in order.
SHEET_FIELDS = [
    "Band", "Album Title", "Spotify", "Youtube Music", "Bandcamp",
    "Referred by", "Genre", "Notes", "Score (out of 10)", "Release Date",
]


def log(msg):
    print(msg, file=sys.stderr, flush=True)


class Throttle:
    """Keep at least `interval` seconds between requests to one service."""

    def __init__(self, interval):
        self.interval = interval
        self.last = 0.0

    def wait(self):
        delay = self.last + self.interval - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        self.last = time.monotonic()


# MusicBrainz allows ~1 request/second; iTunes allows ~20/minute.
MUSICBRAINZ = Throttle(1.2)
ITUNES = Throttle(3.0)


def get_json(url, throttle, retries=4):
    for attempt in range(retries):
        throttle.wait()
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            # 503 is how MusicBrainz says "slow down"; iTunes uses 403/429.
            if e.code in (403, 429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            log(f"    warning: HTTP {e.code} from {urllib.parse.urlsplit(url).netloc}")
            return None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            log(f"    warning: {urllib.parse.urlsplit(url).netloc} failed: {e}")
            return None
    return None


# --- name matching ----------------------------------------------------------


def strip_extras(s):
    """Drop '(Deluxe Edition)', '[Remastered]', and iTunes' ' - EP' / ' - Single'."""
    stripped = re.sub(r"\s+-\s+(EP|Single)$", "", s, flags=re.IGNORECASE)
    stripped = re.sub(r"\s*[(\[][^)\]]*[)\]]", "", stripped).strip()
    return stripped or s


def norm(s):
    s = unicodedata.normalize("NFKD", strip_extras(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.casefold().replace("&", " and ").replace("+", " and ")
    return re.sub(r"[^\w]+", "", s)


def titles_match(a, b):
    a, b = norm(a), norm(b)
    return a == b or difflib.SequenceMatcher(None, a, b).ratio() >= 0.85


def artists_match(a, b):
    # Allow "Clipse" to match "Clipse, Pusha T & Malice".
    a, b = norm(a), norm(b)
    return a == b or a.startswith(b) or b.startswith(a) or difflib.SequenceMatcher(None, a, b).ratio() >= 0.85


# --- MusicBrainz / iTunes ---------------------------------------------------


def lucene_phrase(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def musicbrainz_info(artist, title, album_type):
    query = f"releasegroup:{lucene_phrase(strip_extras(title))} AND artist:{lucene_phrase(artist)}"
    url = "https://musicbrainz.org/ws/2/release-group/?" + urllib.parse.urlencode(
        {"query": query, "fmt": "json", "limit": 10}
    )
    data = get_json(url, MUSICBRAINZ)
    if not data:
        return None

    matches = []
    for rg in data.get("release-groups", []):
        credit = "".join(c.get("name", "") + c.get("joinphrase", "") for c in rg.get("artist-credit", []))
        if titles_match(title, rg.get("title", "")) and artists_match(artist, credit):
            matches.append(rg)
    if not matches:
        return None

    # An album and its lead single often share a name; prefer the same type
    # YouTube Music reports.
    matches.sort(key=lambda rg: (rg.get("primary-type") or "").casefold() != album_type.casefold())
    rg = matches[0]

    detail = get_json(f"https://musicbrainz.org/ws/2/release-group/{rg['id']}?inc=genres&fmt=json", MUSICBRAINZ)
    genres = sorted((detail or {}).get("genres", []), key=lambda g: -g.get("count", 0))
    return {"date": rg.get("first-release-date", ""), "genres": [g["name"] for g in genres]}


def itunes_type(collection_name):
    """iTunes marks singles and EPs with a suffix: 'Doomed Lovers - Single'."""
    m = re.search(r"\s-\s(Single|EP)$", collection_name, flags=re.IGNORECASE)
    return m.group(1) if m else "Album"


def itunes_info(artist, title, album_type):
    url = "https://itunes.apple.com/search?" + urllib.parse.urlencode(
        {"term": f"{artist} {strip_extras(title)}", "entity": "album", "limit": 10}
    )
    data = get_json(url, ITUNES)
    matches = [
        r
        for r in (data or {}).get("results", [])
        if titles_match(title, r.get("collectionName", "")) and artists_match(artist, r.get("artistName", ""))
    ]
    if not matches:
        return None
    # Same as MusicBrainz: prefer the type YouTube Music reports, so an album
    # doesn't get its same-named lead single's date.
    matches.sort(key=lambda r: itunes_type(r.get("collectionName", "")).casefold() != album_type.casefold())
    genre = matches[0].get("primaryGenreName")
    return {"date": matches[0].get("releaseDate", "")[:10], "genres": [genre] if genre else []}


# --- YouTube Music ----------------------------------------------------------


def playlist_id(url_or_id):
    s = url_or_id.strip()
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(s).query)
    if "list" in query:
        return query["list"][0]
    if re.fullmatch(r"[A-Za-z0-9_-]{10,}", s):
        return s
    raise ValueError(f"Can't find a playlist id in: {url_or_id}")


def art_url(thumbnails, size):
    if not thumbnails:
        return ""
    url = thumbnails[-1]["url"]
    suffix = "=s0" if size == 0 else f"=w{size}-h{size}-l90-rj"
    return re.sub(r"=w\d+-h\d+.*$", suffix, url)


def join_artists(artists):
    return " & ".join(a["name"] for a in artists or [] if a.get("name"))


def album_from_track(yt, track, art_size):
    """Album details from YouTube Music, falling back to what the track has."""
    album_ref = track["album"]
    info = {
        "Band": join_artists(track.get("artists")),
        "Album Title": album_ref.get("name", ""),
        "Type": "",
        "year": "",
        "songs": set(),  # normalized song titles, for matching singles to albums
        "Album Art": art_url(track.get("thumbnails"), art_size),
        "Youtube Music": f"https://music.youtube.com/browse/{album_ref['id']}",
    }
    try:
        album = yt.get_album(album_ref["id"])
    except Exception as e:
        log(f"    warning: couldn't load album page ({e}), using track info")
        return info

    info["Band"] = join_artists(album.get("artists")) or info["Band"]
    info["Album Title"] = album.get("title") or info["Album Title"]
    info["Type"] = album.get("type", "")
    info["year"] = album.get("year") or ""
    info["Album Art"] = art_url(album.get("thumbnails"), art_size) or info["Album Art"]
    info["songs"] = {norm(t["title"]) for t in album.get("tracks") or [] if t.get("title")}
    if album.get("audioPlaylistId"):
        info["Youtube Music"] = f"https://music.youtube.com/playlist?list={album['audioPlaylistId']}"
    return info


def pick_date(itunes_date, mb_date, yt_year):
    # Take the first full date whose year agrees with YouTube Music's, which
    # catches a wrong match or a bad entry on either site. iTunes goes first: it
    # has the official street date, while MusicBrainz uses the earliest edition
    # it knows of (promos, pre-orders), which can be a few days early.
    for date in (itunes_date, mb_date):
        if date and (not yt_year or date[:4] == yt_year):
            return date
    return yt_year or itunes_date or mb_date


ACRONYMS = {"ebm", "edm", "idm", "uk", "us", "nwobhm", "dsbm", "r&b"}


def format_genres(genres):
    """['doom metal', 'metal', 'post-metal'] -> 'Doom Metal / Post Metal', the sheet's style."""
    names = []
    for genre in genres:
        for part in genre.split("/"):  # iTunes: "Death Metal/Black Metal"
            words = part.replace("-", " ").split()
            name = " ".join(w.upper() if w.casefold() in ACRONYMS else w[:1].upper() + w[1:] for w in words)
            if name and name.casefold() not in (n.casefold() for n in names):
                names.append(name)
    # Drop a broad genre when a narrower one covers it ("Metal" next to "Doom Metal").
    names = [n for n in names if not any(o.casefold().endswith(" " + n.casefold()) for o in names)]
    return " / ".join(names[:MAX_GENRES])


def add_date_and_genre(info):
    artist, title = info["Band"], info["Album Title"]
    mb = musicbrainz_info(artist, title, info["Type"]) or {}
    it = itunes_info(artist, title, info["Type"]) or {}

    info["Release Date"] = pick_date(it.get("date", ""), mb.get("date", ""), info["year"])
    # MusicBrainz genres are specific ("blackened death metal"); iTunes is broad ("Metal").
    info["Genre"] = format_genres(mb.get("genres") or it.get("genres") or [])
    return info


def find_album_for_song(release, song_title, full_albums):
    """The full album by the same artist that has this song, if it's in the playlist."""
    song = norm(song_title)
    for album in full_albums:
        if album is not release and song in album["songs"] and artists_match(album["Band"], release["Band"]):
            return album
    return None


def collect_albums(urls, art_size):
    """Unique albums in playlist order, from YouTube Music only."""
    yt = YTMusic()
    tracks, skipped = [], []
    for url in urls:
        pid = playlist_id(url)
        try:
            playlist = yt.get_playlist(pid, limit=None)
        except Exception:
            raise ValueError(f"Couldn't load playlist {pid}. Is it public (or unlisted) and is the URL right?")
        log(f'Playlist "{playlist.get("title", pid)}": {len(playlist.get("tracks", []))} tracks')
        for track in playlist.get("tracks", []):
            if (track.get("album") or {}).get("id"):
                tracks.append(track)
            else:
                skipped.append(f'{join_artists(track.get("artists"))} - {track.get("title")}')

    releases = {}
    for track in tracks:
        album_id = track["album"]["id"]
        if album_id not in releases:
            releases[album_id] = album_from_track(yt, track, art_size)
    full_albums = [r for r in releases.values() if r["Type"] == "Album"]

    albums, position, merged = [], {}, set()
    for track in tracks:
        release = releases[track["album"]["id"]]
        # Songs that came out as singles (or on an EP) before the album often
        # still point at the single in a playlist. Count them as part of the
        # album when the album is in the playlist too.
        if release["Type"] != "Album":
            album = find_album_for_song(release, track.get("title", ""), full_albums)
            if album:
                label = f'{release["Band"]} - {release["Album Title"]} ({release["Type"]})'
                if label not in merged:
                    merged.add(label)
                    log(f'  {label}: counted as part of the album {album["Album Title"]}')
                release = album

        # The same album can show up under more than one id (e.g. explicit and
        # clean versions, or a single named after the album). Keep the album.
        key = (norm(release["Band"]), norm(release["Album Title"]))
        if key not in position:
            position[key] = len(albums)
            albums.append(release)
        elif release["Type"] == "Album" and albums[position[key]]["Type"] != "Album":
            albums[position[key]] = release

    if skipped:
        log(f"Skipped {len(skipped)} track(s) with no album on YouTube Music (uploads or plain videos):")
        for s in skipped:
            log(f"  - {s}")
    return albums


def gather(urls, art_size):
    albums = collect_albums(urls, art_size)
    for i, info in enumerate(albums, 1):
        log(f'  [{i}/{len(albums)}] {info["Band"]} - {info["Album Title"]}')
        add_date_and_genre(info)
    return albums


# Letters that don't split into base letter + accent.
LATIN_FOLD = str.maketrans(
    {"Æ": "Ae", "æ": "ae", "Ø": "O", "ø": "o", "Œ": "Oe", "œ": "oe", "ß": "ss",
     "Þ": "Th", "þ": "th", "Ð": "D", "ð": "d", "Ł": "L", "ł": "l"}
)


def camel_case(s):
    """'Florence + The Machine' -> 'FlorenceAndTheMachine', the naming used for post images."""
    s = re.sub(r"['’`]", "", s.replace("&", " and ").replace("+", " and "))  # Ba'al -> Baal
    folded = unicodedata.normalize("NFKD", s.translate(LATIN_FOLD))
    folded = "".join(c for c in folded if not unicodedata.combining(c))  # Tómarúm -> Tomarum
    # Names with no Latin letters (e.g. Cyrillic) keep their own script.
    words = re.findall(r"[A-Za-z0-9]+", folded) or re.findall(r"[^\W_]+", s)
    # HAIM -> Haim, but keep mixed case like DHiver as is.
    return "".join(w.capitalize() if w.isupper() and len(w) > 1 else w[0].upper() + w[1:] for w in words)


def download_art(albums, folder):
    os.makedirs(folder, exist_ok=True)
    log(f"\nDownloading album art to {folder}")
    band_counts = Counter(camel_case(a["Band"]) for a in albums)
    for a in albums:
        label = f'{a["Band"]} - {a["Album Title"]}'
        name = camel_case(a["Band"])
        if band_counts[name] > 1 or not name:
            name += camel_case(a["Album Title"])
        if not name or not a["Album Art"]:
            log(f"  warning: no art or file name for {label}, skipping")
            continue

        filename = name + ".jpg"
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            log(f"  {filename} already exists, skipping")
            continue
        try:
            req = urllib.request.Request(a["Album Art"], headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
        except (urllib.error.URLError, TimeoutError) as e:
            log(f"  warning: couldn't download art for {label}: {e}")
            continue
        with open(path, "wb") as f:
            f.write(data)
        log(f"  {filename}  ({label})")


def write(albums, fmt, out, header=False):
    if fmt in ("csv", "tsv"):
        writer = csv.DictWriter(
            out,
            fieldnames=SHEET_FIELDS,
            restval="",  # Spotify, Bandcamp, Referred by, Notes, Score
            extrasaction="ignore",  # art URL, type
            delimiter="\t" if fmt == "tsv" else ",",
            lineterminator="\n",
        )
        if header:
            writer.writeheader()
        for a in albums:
            # The sheet tracks release month: 2026-01-16 -> 2026-01.
            writer.writerow({**a, "Release Date": a["Release Date"][:7]})
        return
    for i, a in enumerate(albums, 1):
        details = " · ".join(x for x in (a["Release Date"], a["Type"], a["Genre"]) if x)
        print(f'{i}. {a["Band"]} - {a["Album Title"]}', file=out)
        print(f"   {details}", file=out)
        print(f'   art: {a["Album Art"]}', file=out)
        print(f'   ytm: {a["Youtube Music"]}', file=out)


def main():
    parser = argparse.ArgumentParser(
        description="List unique albums in YouTube Music playlists, in playlist order, "
        "with release date, genre, and album art URL."
    )
    parser.add_argument("urls", nargs="*", help="playlist URL(s) or id(s); prompts if none given")
    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "csv", "tsv"],
        default="text",
        help="text (default), or csv/tsv rows matching the Music Listening sheet's columns",
    )
    parser.add_argument("-o", "--output", help="write to this file instead of stdout")
    parser.add_argument(
        "--header", action="store_true", help="include the column names as the first csv/tsv row"
    )
    parser.add_argument(
        "--art-size",
        type=int,
        default=544,
        help="album art size in pixels (default 544, same as past posts; 0 = original, usually 1200+)",
    )
    parser.add_argument(
        "--download-art",
        metavar="DIR",
        help="save album art into DIR as BandName.jpg, like past posts' images (existing files are left alone)",
    )
    args = parser.parse_args()

    urls = args.urls or [input("Paste a YouTube Music playlist URL: ").strip()]
    try:
        albums = gather(urls, args.art_size)
    except ValueError as e:
        sys.exit(str(e))

    if args.download_art:
        download_art(albums, args.download_art)

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            write(albums, args.format, f, args.header)
        log(f"\nWrote {len(albums)} albums to {args.output}")
    else:
        if args.format == "text":
            log("")
        write(albums, args.format, sys.stdout, args.header)


if __name__ == "__main__":
    main()
