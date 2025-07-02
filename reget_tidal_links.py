import os
import csv
import tidalapi
import webbrowser
import re

def login_tidal():
    """Login to Tidal using OAuth"""
    session = tidalapi.Session()
    login, future = session.login_oauth()
    webbrowser.open(login.verification_uri_complete)
    print(f"\n→ Complete Tidal login here: {login.verification_uri_complete}\n")
    future.result()
    if not session.check_login():
        raise RuntimeError("❌ Tidal OAuth failed")
    print("✅ Logged into Tidal\n")
    return session

def search_tidal_tracks(session, title, artist, max_results=10):
    """Search for tracks on Tidal and return list of results"""
    clean_title = re.sub(r'\((?:feat\.?|featuring|ft\.?|with)[^)]*\)', '', title).strip().lower()
    query = f"{clean_title} {artist}"
    search = session.search(query, models=[tidalapi.Track])
    tracks = search.get("tracks", [])
    return tracks[:max_results]  # Limit results

def search_tidal_albums(session, album_name, artist, max_results=10):
    """Search for albums on Tidal and return list of results"""
    query = f"{album_name} {artist}"
    search = session.search(query, models=[tidalapi.Album])
    albums = search.get("albums", [])
    return albums[:max_results]  # Limit results

def display_track_options(tracks):
    """Display track options with numbers"""
    if not tracks:
        print("  ❌ No results found")
        return None
    
    print(f"  Found {len(tracks)} results:")
    for i, track in enumerate(tracks, 1):
        duration_minutes = track.duration // 60
        duration_seconds = track.duration % 60
        
        # Get all artists (handle multiple artists)
        if hasattr(track, 'artists') and track.artists:
            artist_names = [artist.name for artist in track.artists]
            artist_display = ", ".join(artist_names)
        else:
            artist_display = track.artist.name
        
        print(f"  {i:2d}. {track.name} - {artist_display} ({duration_minutes}:{duration_seconds:02d})")
    
    return tracks

def display_album_options(albums):
    """Display album options with numbers"""
    if not albums:
        print("  ❌ No results found")
        return None
    
    print(f"  Found {len(albums)} results:")
    for i, album in enumerate(albums, 1):
        year = getattr(album, 'year', 'Unknown')
        num_tracks = getattr(album, 'num_tracks', 'Unknown')
        
        # Get all artists (handle multiple artists)
        if hasattr(album, 'artists') and album.artists:
            artist_names = [artist.name for artist in album.artists]
            artist_display = ", ".join(artist_names)
        else:
            artist_display = album.artist.name
        
        print(f"  {i:2d}. {album.name} - {artist_display} ({year}, {num_tracks} tracks)")
    
    return albums

def get_user_choice(max_option):
    """Get user's choice from numbered options"""
    while True:
        try:
            choice = input(f"  Select option (1-{max_option}, or 0 to skip): ").strip()
            if choice == '0':
                return 0
            choice_num = int(choice)
            if 1 <= choice_num <= max_option:
                return choice_num
            else:
                print(f"  Please enter a number between 1 and {max_option}, or 0 to skip")
        except ValueError:
            print("  Please enter a valid number")
        except KeyboardInterrupt:
            print("\n  Operation cancelled")
            return 0

def read_not_found_tracks(filename="not_found_tracks.txt"):
    """Read not found tracks from file"""
    tracks = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and " — " in line:
                    # Check if duration is included in parentheses at the end
                    duration = None
                    if line.endswith(")") and "(" in line:
                        # Extract duration from parentheses
                        parts = line.rsplit("(", 1)
                        if len(parts) == 2:
                            main_part = parts[0].strip()
                            duration_part = parts[1].rstrip(")")
                            # Validate duration format (m:ss)
                            if ":" in duration_part and duration_part.replace(":", "").isdigit():
                                duration = duration_part
                                line = main_part
                    
                    # Split on " — " to separate title and artist
                    parts = line.split(" — ", 1)
                    if len(parts) == 2:
                        title, artist = parts
                        tracks.append((title.strip(), artist.strip(), duration))
        print(f"📖 Read {len(tracks)} not found tracks from {filename}")
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
    return tracks

def read_not_found_albums(filename="not_found_albums.txt"):
    """Read not found albums from file"""
    albums = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and " — " in line:
                    # Split on " — " to separate album and artist
                    parts = line.split(" — ", 1)
                    if len(parts) == 2:
                        album_name, artist = parts
                        albums.append((album_name.strip(), artist.strip()))
        print(f"📖 Read {len(albums)} not found albums from {filename}")
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
    return albums

def process_tracks_interactively(session, tracks):
    """Process tracks with interactive selection"""
    found_tracks = []
    skipped_tracks = []
    
    print(f"\n🎵 Processing {len(tracks)} tracks interactively...")
    print("=" * 60)
    
    for i, track_info in enumerate(tracks, 1):
        if len(track_info) == 3:
            title, artist, duration = track_info
            duration_display = f" ({duration})" if duration else ""
        else:
            title, artist = track_info
            duration_display = ""
        
        print(f"\n[{i}/{len(tracks)}] Searching: {title} — {artist}{duration_display}")
        
        # Search for tracks
        results = search_tidal_tracks(session, title, artist)
        displayed_tracks = display_track_options(results)
        
        if displayed_tracks:
            choice = get_user_choice(len(displayed_tracks))
            if choice > 0:
                selected_track = displayed_tracks[choice - 1]
                url = f"https://tidal.com/browse/track/{selected_track.id}"
                
                # Get all artists for display
                if hasattr(selected_track, 'artists') and selected_track.artists:
                    artist_names = [artist.name for artist in selected_track.artists]
                    artist_display = ", ".join(artist_names)
                else:
                    artist_display = selected_track.artist.name
                
                found_tracks.append([
                    artist,                    # Spotify Artist
                    selected_track.artist.name, # Tidal Artist (primary)
                    title,                     # Spotify Title
                    selected_track.name,       # Tidal Title
                    url                        # Tidal URL
                ])
                print(f"  ✅ Selected: {selected_track.name} - {artist_display}")
            else:
                # Preserve original format when skipping
                original_format = f"{title} — {artist}{duration_display}"
                skipped_tracks.append(original_format)
                print(f"  ⏭️  Skipped")
        else:
            # Preserve original format when no results found
            original_format = f"{title} — {artist}{duration_display}"
            skipped_tracks.append(original_format)
            print(f"  ⏭️  No results, skipped")
    
    return found_tracks, skipped_tracks

def process_albums_interactively(session, albums):
    """Process albums with interactive selection"""
    found_albums = []
    skipped_albums = []
    
    print(f"\n💿 Processing {len(albums)} albums interactively...")
    print("=" * 60)
    
    for i, (album_name, artist) in enumerate(albums, 1):
        print(f"\n[{i}/{len(albums)}] Searching: {album_name} — {artist}")
        
        # Search for albums
        results = search_tidal_albums(session, album_name, artist)
        displayed_albums = display_album_options(results)
        
        if displayed_albums:
            choice = get_user_choice(len(displayed_albums))
            if choice > 0:
                selected_album = displayed_albums[choice - 1]
                url = f"https://tidal.com/browse/album/{selected_album.id}"
                
                # Get all artists for display
                if hasattr(selected_album, 'artists') and selected_album.artists:
                    artist_names = [artist.name for artist in selected_album.artists]
                    artist_display = ", ".join(artist_names)
                else:
                    artist_display = selected_album.artist.name
                
                found_albums.append([
                    artist,                     # Spotify Artist
                    selected_album.artist.name, # Tidal Artist (primary)
                    album_name,                 # Spotify Title
                    selected_album.name,        # Tidal Title
                    url                         # Tidal URL
                ])
                print(f"  ✅ Selected: {selected_album.name} - {artist_display}")
            else:
                skipped_albums.append(f"{album_name} — {artist}")
                print(f"  ⏭️  Skipped")
        else:
            skipped_albums.append(f"{album_name} — {artist}")
            print(f"  ⏭️  No results, skipped")
    
    return found_albums, skipped_albums

def save_results(found_tracks, found_albums, skipped_tracks, skipped_albums):
    """Save results to CSV files and update not found files"""
    
    # Save found tracks to CSV (append to existing file)
    if found_tracks:
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists("tidal_track_links.csv")
        
        with open("tidal_track_links.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Spotify Artist", "Tidal Artist", "Spotify Title", "Tidal Title", "Tidal URL"])
            writer.writerows(found_tracks)
        print(f"✅ Added {len(found_tracks)} tracks to tidal_track_links.csv")
    
    # Save found albums to CSV (append to existing file)
    if found_albums:
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists("tidal_album_links.csv")
        
        with open("tidal_album_links.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Spotify Artist", "Tidal Artist", "Spotify Title", "Tidal Title", "Tidal URL"])
            writer.writerows(found_albums)
        print(f"✅ Added {len(found_albums)} albums to tidal_album_links.csv")
    
    # Update not found tracks file
    if skipped_tracks:
        with open("not_found_tracks_again.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(skipped_tracks))
        print(f"📝 Updated not_found_tracks_again.txt with {len(skipped_tracks)} remaining tracks")
    
    # Update not found albums file
    if skipped_albums:
        with open("not_found_albums_again.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(skipped_albums))
        print(f"📝 Updated not_found_albums_again.txt with {len(skipped_albums)} remaining albums")

def main():
    print("🔍 Interactive Tidal Link Recovery Tool")
    print("=" * 40)
    
    # Login to Tidal
    try:
        session = login_tidal()
    except Exception as e:
        print(f"❌ Failed to login to Tidal: {e}")
        return
    
    # Ask user what they want to process
    print("What would you like to process?")
    print("1. Tracks only")
    print("2. Albums only") 
    print("3. Both tracks and albums")
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                break
            else:
                print("Please enter 1, 2, or 3")
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return
    
    found_tracks = []
    found_albums = []
    skipped_tracks = []
    skipped_albums = []
    
    # Process tracks
    if choice in ['1', '3']:
        tracks = read_not_found_tracks()
        if tracks:
            found_tracks, skipped_tracks = process_tracks_interactively(session, tracks)
    
    # Process albums
    if choice in ['2', '3']:
        albums = read_not_found_albums()
        if albums:
            found_albums, skipped_albums = process_albums_interactively(session, albums)
    
    # Save results
    save_results(found_tracks, found_albums, skipped_tracks, skipped_albums)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    if choice in ['1', '3']:
        print(f"🎵 Tracks: {len(found_tracks)} found, {len(skipped_tracks)} skipped")
    if choice in ['2', '3']:
        print(f"💿 Albums: {len(found_albums)} found, {len(skipped_albums)} skipped")
    print("✅ Process completed!")

if __name__ == "__main__":
    main()
