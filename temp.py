import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ── Configuration ────────────────────────────────────────────────────
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI  = os.getenv("SPOTIPY_REDIRECT_URI")
SPOTIFY_SCOPE         = "playlist-read-private"

def setup_spotify():
    """Setup Spotify client"""
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id     = SPOTIFY_CLIENT_ID,
        client_secret = SPOTIFY_CLIENT_SECRET,
        redirect_uri  = SPOTIFY_REDIRECT_URI,
        scope         = SPOTIFY_SCOPE
    ))
    return sp

def search_spotify_track(sp, title, artist):
    """Search for a track on Spotify and return duration"""
    query = f'track:"{title}" artist:"{artist}"'
    results = sp.search(q=query, type='track', limit=10)
    
    tracks = results['tracks']['items']
    
    # Try to find exact match first
    for track in tracks:
        track_name = track['name'].lower()
        track_artist = track['artists'][0]['name'].lower()
        
        if (title.lower() in track_name or track_name in title.lower()) and \
           (artist.lower() in track_artist or track_artist in artist.lower()):
            duration_ms = track['duration_ms']
            duration_minutes = duration_ms // 60000
            duration_seconds = (duration_ms % 60000) // 1000
            duration_str = f"{duration_minutes}:{duration_seconds:02d}"
            return duration_str
    
    # If no exact match, try broader search
    query = f"{title} {artist}"
    results = sp.search(q=query, type='track', limit=5)
    tracks = results['tracks']['items']
    
    if tracks:
        # Return the first result's duration
        track = tracks[0]
        duration_ms = track['duration_ms']
        duration_minutes = duration_ms // 60000
        duration_seconds = (duration_ms % 60000) // 1000
        duration_str = f"{duration_minutes}:{duration_seconds:02d}"
        return duration_str
    
    return None

def read_not_found_tracks(filename="not_found_tracks.txt"):
    """Read not found tracks from file"""
    tracks = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and " — " in line:
                    # Check if duration is already included
                    if line.endswith(")") and "(" in line:
                        # Duration already exists, keep as is
                        tracks.append(line)
                    else:
                        # Split on " — " to separate title and artist
                        parts = line.split(" — ", 1)
                        if len(parts) == 2:
                            title, artist = parts
                            tracks.append((title.strip(), artist.strip()))
        print(f"📖 Read {len(tracks)} tracks from {filename}")
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
    return tracks

def main():
    print("🔍 Temporary Duration Updater for not_found_tracks.txt")
    print("=" * 50)
    
    # Setup Spotify
    try:
        sp = setup_spotify()
        print("✅ Connected to Spotify")
    except Exception as e:
        print(f"❌ Failed to connect to Spotify: {e}")
        return
    
    # Read existing tracks
    tracks = read_not_found_tracks()
    if not tracks:
        print("No tracks to process")
        return
    
    updated_tracks = []
    processed_count = 0
    found_duration_count = 0
    
    print(f"\n🎵 Processing {len(tracks)} tracks...")
    print("=" * 50)
    
    for i, track_info in enumerate(tracks, 1):
        if isinstance(track_info, tuple):
            # Track needs duration lookup
            title, artist = track_info
            print(f"[{i}/{len(tracks)}] Searching: {title} — {artist}")
            
            duration = search_spotify_track(sp, title, artist)
            if duration:
                updated_line = f"{title} — {artist} ({duration})"
                updated_tracks.append(updated_line)
                found_duration_count += 1
                print(f"  ✅ Found duration: {duration}")
            else:
                updated_line = f"{title} — {artist}"
                updated_tracks.append(updated_line)
                print(f"  ❌ Duration not found")
            
            processed_count += 1
        else:
            # Track already has duration, keep as is
            updated_tracks.append(track_info)
            print(f"[{i}/{len(tracks)}] Keeping: {track_info}")
    
    # Write updated tracks back to file
    try:
        with open("not_found_tracks_updated.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(updated_tracks))
        print(f"\n✅ Updated file saved as: not_found_tracks_updated.txt")
        
        # Also backup original and replace it
        import shutil
        shutil.copy("not_found_tracks.txt", "not_found_tracks_backup.txt")
        shutil.copy("not_found_tracks_updated.txt", "not_found_tracks.txt")
        print(f"✅ Original file backed up as: not_found_tracks_backup.txt")
        print(f"✅ Updated file replaced: not_found_tracks.txt")
        
    except Exception as e:
        print(f"❌ Failed to write file: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"📝 Total tracks processed: {len(tracks)}")
    print(f"🔍 Tracks searched: {processed_count}")
    print(f"⏱️  Durations found: {found_duration_count}")
    print(f"❌ Durations not found: {processed_count - found_duration_count}")
    print("✅ Process completed!")

if __name__ == "__main__":
    main()
