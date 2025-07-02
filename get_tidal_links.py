import os
import csv
import spotipy
import tidalapi
import webbrowser
import re
from spotipy.oauth2 import SpotifyOAuth

# ── Configuration ────────────────────────────────────────────────────
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI  = os.getenv("SPOTIPY_REDIRECT_URI")
SPOTIFY_SCOPE         = "playlist-read-private"

# Paste your playlist links here:
raw_individual_playlist = "https://open.spotify.com/playlist/5epr9yWDpDeQ88iirjoEjG?si=27a32f8107b34cbd"
raw_album_playlist      = "https://open.spotify.com/playlist/4dftFNxIPR76I0qAzGDA0s?si=1590c43ba3dc4acd"

individual_playlist_id = raw_individual_playlist.split("?", 1)[0].split("/")[-1]
album_playlist_id      = raw_album_playlist.split("?", 1)[0].split("/")[-1]

# ── Spotify: Fetch Playlist Tracks ───────────────────────────────────
def fetch_spotify_tracks(playlist_id):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id     = SPOTIFY_CLIENT_ID,
        client_secret = SPOTIFY_CLIENT_SECRET,
        redirect_uri  = SPOTIFY_REDIRECT_URI,
        scope         = SPOTIFY_SCOPE
    ))
    all_items = []
    results = sp.playlist_tracks(playlist_id)
    all_items.extend(results["items"])
    while results["next"]:
        results = sp.next(results)
        all_items.extend(results["items"])
    return all_items

# ── Tidal: OAuth login & search ──────────────────────────────────────
def login_tidal():
    session = tidalapi.Session()
    login, future = session.login_oauth()
    webbrowser.open(login.verification_uri_complete)
    print(f"\n→ Complete Tidal login here: {login.verification_uri_complete}\n")
    future.result()
    if not session.check_login():
        raise RuntimeError("❌ Tidal OAuth failed")
    print("✅ Logged into Tidal\n")
    return session

def find_tidal_track(session, title, artist):
    query = f"{title} {artist}"
    search = session.search(query, models=[tidalapi.Track])
    tracks = search.get("tracks", [])
    
    # Remove "(feat. ...)", "(featuring ...)", "(ft. ...)", "(with ...)" parts from title for matching
    clean_title = re.sub(r'\((?:feat\.?|featuring|ft\.?|with)[^)]*\)', '', title).strip().lower()
    
    for track in tracks:
        # Clean the Tidal track name too
        clean_tidal_title = re.sub(r'\((?:feat\.?|featuring|ft\.?|with)[^)]*\)', '', track.name).strip().lower()
        
        # match artist and title loosely
        if (artist.lower() in track.artist.name.lower() and 
            clean_title in clean_tidal_title):
            url = f"https://tidal.com/browse/track/{track.id}"
            return track, url
    return None

def find_tidal_album(session, album_name, artist):
    query = f"{album_name} {artist}"
    search = session.search(query, models=[tidalapi.Album])
    albums = search.get("albums", [])
    for alb in albums:
        # match artist and album name loosely
        if (artist.lower() in alb.artist.name.lower() and
            album_name.lower() in alb.name.lower()):
            url = f"https://tidal.com/browse/album/{alb.id}"
            return alb, url
    return None

# ── Main ──────────────────────────────────────────────────────────────
def main():
    print("🔍 Fetching Spotify individual-track playlist…")
    tracks = fetch_spotify_tracks(individual_playlist_id)
    print(f"  ▶️  Found {len(tracks)} tracks\n")

    print("🔍 Fetching Spotify album-playlist…")
    album_items = fetch_spotify_tracks(album_playlist_id)
    print(f"  ▶️  Found {len(album_items)} tracks (from which we'll extract albums)\n")

    tidal = login_tidal()

    # ── 1) TRACK-LEVEL SEARCH ─────────────────────────────────────────
    track_rows = []
    missing_tracks = []

    print("🔍 Searching Tidal for each individual track…")
    for item in tracks:
        sp_track  = item["track"]
        sp_title   = sp_track["name"]
        sp_artist  = sp_track["artists"][0]["name"]
        sp_duration_ms = sp_track["duration_ms"]
        
        # Convert duration from milliseconds to minutes:seconds
        sp_duration_minutes = sp_duration_ms // 60000
        sp_duration_seconds = (sp_duration_ms % 60000) // 1000
        sp_duration_str = f"{sp_duration_minutes}:{sp_duration_seconds:02d}"
        
        print(f"• {sp_title} — {sp_artist}", end="  ")

        res = find_tidal_track(tidal, sp_title, sp_artist)
        if res:
            td_track, url = res
            td_title  = td_track.name
            td_artist = td_track.artist.name
            print(f"→ {td_title}")
            track_rows.append([
                sp_artist,
                td_artist,
                sp_title,
                td_title,
                url
            ])
        else:
            print("→ ❌ Not found")
            missing_tracks.append(f"{sp_title} — {sp_artist} ({sp_duration_str})")

    with open("tidal_track_links.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Spotify Artist","Tidal Artist","Spotify Title","Tidal Title","Tidal URL"])
        w.writerows(track_rows)

    with open("not_found_tracks.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(missing_tracks))

    print(f"\n✅ Track search done: {len(track_rows)} found, {len(missing_tracks)} missing.")
    print(" • Tracks → tidal_track_links.csv")
    print(" • Missing → not_found_tracks.txt\n")

    # ── 2) ALBUM-LEVEL SEARCH ─────────────────────────────────────────
    # build set of unique (album_name, album_artist)
    unique = {}
    for item in album_items:
        sp_album  = item["track"]["album"]["name"]
        sp_artist = item["track"]["album"]["artists"][0]["name"]
        unique[(sp_album, sp_artist)] = True

    album_rows = []
    missing_albums = []

    print("🔍 Searching Tidal for each unique album…")
    for (sp_album, sp_artist) in unique:
        print(f"• {sp_album} — {sp_artist}", end="  ")
        res = find_tidal_album(tidal, sp_album, sp_artist)
        if res:
            td_album, url = res
            td_name   = td_album.name
            td_artist = td_album.artist.name
            print(f"→ {td_name}")
            album_rows.append([
                sp_artist,
                td_artist,
                sp_album,
                td_name,
                url
            ])
        else:
            print("→ ❌ Not found")
            missing_albums.append(f"{sp_album} — {sp_artist}")

    with open("tidal_album_links.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Spotify Artist","Tidal Artist","Spotify Title","Tidal Title","Tidal URL"])
        w.writerows(album_rows)

    with open("not_found_albums.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(missing_albums))

    print(f"\n✅ Album search done: {len(album_rows)} found, {len(missing_albums)} missing.")
    print(" • Albums → tidal_album_links.csv")
    print(" • Missing → not_found_albums.txt")

if __name__ == "__main__":
    main()
