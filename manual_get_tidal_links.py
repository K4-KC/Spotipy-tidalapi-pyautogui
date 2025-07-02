import os
import csv
import re

def read_manual_tracks(filename="not_found_tracks_again.txt"):
    """Read tracks with manually added links from file"""
    tracks_with_links = []
    tracks_without_links = []
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Check if line contains a URL (basic URL pattern matching)
                url_pattern = r'https?://[^\s]+'
                urls = re.findall(url_pattern, line)
                
                if urls:
                    # Extract the URL (take the last one if multiple found)
                    url = urls[-1]
                    
                    # Remove the URL from the line to get the track info
                    track_info = re.sub(url_pattern, '', line).strip()
                    
                    # Parse track info: "Title — Artist (duration)"
                    if " — " in track_info:
                        # Check if duration is included in parentheses
                        duration = None
                        if track_info.endswith(")") and "(" in track_info:
                            # Extract duration from parentheses
                            parts = track_info.rsplit("(", 1)
                            if len(parts) == 2:
                                track_info = parts[0].strip()
                                duration_part = parts[1].rstrip(")")
                                # Validate duration format (m:ss)
                                if ":" in duration_part and duration_part.replace(":", "").isdigit():
                                    duration = duration_part
                        
                        # Split on " — " to separate title and artist
                        parts = track_info.split(" — ", 1)
                        if len(parts) == 2:
                            title, artist = parts
                            tracks_with_links.append({
                                'title': title.strip(),
                                'artist': artist.strip(),
                                'duration': duration,
                                'url': url,
                                'line_num': line_num,
                                'original_line': line
                            })
                        else:
                            print(f"⚠️  Line {line_num}: Could not parse track info from '{track_info}'")
                    else:
                        print(f"⚠️  Line {line_num}: No ' — ' separator found in '{track_info}'")
                else:
                    # No URL found, keep as not found
                    tracks_without_links.append(line)
        
        print(f"📖 Read {len(tracks_with_links)} tracks with links and {len(tracks_without_links)} without links from {filename}")
        
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
        return [], []
    except Exception as e:
        print(f"❌ Error reading file {filename}: {e}")
        return [], []
    
    return tracks_with_links, tracks_without_links

def read_manual_albums(filename="not_found_albums_again.txt"):
    """Read albums with manually added links from file"""
    albums_with_links = []
    albums_without_links = []
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Check if line contains a URL (basic URL pattern matching)
                url_pattern = r'https?://[^\s]+'
                urls = re.findall(url_pattern, line)
                
                if urls:
                    # Extract the URL (take the last one if multiple found)
                    url = urls[-1]
                    
                    # Remove the URL from the line to get the album info
                    album_info = re.sub(url_pattern, '', line).strip()
                    
                    # Parse album info: "Album Name — Artist"
                    if " — " in album_info:
                        # Split on " — " to separate album name and artist
                        parts = album_info.split(" — ", 1)
                        if len(parts) == 2:
                            album_name, artist = parts
                            albums_with_links.append({
                                'album_name': album_name.strip(),
                                'artist': artist.strip(),
                                'url': url,
                                'line_num': line_num,
                                'original_line': line
                            })
                        else:
                            print(f"⚠️  Line {line_num}: Could not parse album info from '{album_info}'")
                    else:
                        print(f"⚠️  Line {line_num}: No ' — ' separator found in '{album_info}'")
                else:
                    # No URL found, keep as not found
                    albums_without_links.append(line)
        
        print(f"📖 Read {len(albums_with_links)} albums with links and {len(albums_without_links)} without links from {filename}")
        
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
        return [], []
    except Exception as e:
        print(f"❌ Error reading file {filename}: {e}")
        return [], []
    
    return albums_with_links, albums_without_links

def append_tracks_to_csv(tracks_with_links, csv_filename="tidal_track_links.csv"):
    """Append found tracks to the CSV file"""
    if not tracks_with_links:
        return 0
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(csv_filename)
    
    try:
        with open(csv_filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header if file doesn't exist
            if not file_exists:
                writer.writerow(["Spotify Artist", "Tidal Artist", "Spotify Title", "Tidal Title", "Tidal URL"])
            
            # Write each track
            for track in tracks_with_links:
                writer.writerow([
                    track['artist'],        # Spotify Artist
                    track['artist'],        # Tidal Artist (same as Spotify since manually found)
                    track['title'],         # Spotify Title
                    track['title'],         # Tidal Title (same as Spotify since manually found)
                    track['url']           # URL (could be Tidal, Amazon Music, Deezer, etc.)
                ])
        
        print(f"✅ Added {len(tracks_with_links)} tracks to {csv_filename}")
        return len(tracks_with_links)
        
    except Exception as e:
        print(f"❌ Error writing to {csv_filename}: {e}")
        return 0

def append_albums_to_csv(albums_with_links, csv_filename="tidal_album_links.csv"):
    """Append found albums to the CSV file"""
    if not albums_with_links:
        return 0
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(csv_filename)
    
    try:
        with open(csv_filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header if file doesn't exist
            if not file_exists:
                writer.writerow(["Spotify Artist", "Tidal Artist", "Spotify Title", "Tidal Title", "Tidal URL"])
            
            # Write each album
            for album in albums_with_links:
                writer.writerow([
                    album['artist'],        # Spotify Artist
                    album['artist'],        # Tidal Artist (same as Spotify since manually found)
                    album['album_name'],    # Spotify Title (Album Name)
                    album['album_name'],    # Tidal Title (same as Spotify since manually found)
                    album['url']           # URL (could be Tidal, Amazon Music, Deezer, etc.)
                ])
        
        print(f"✅ Added {len(albums_with_links)} albums to {csv_filename}")
        return len(albums_with_links)
        
    except Exception as e:
        print(f"❌ Error writing to {csv_filename}: {e}")
        return 0

def update_not_found_tracks(tracks_without_links, output_filename="not_found_tracks_again.txt"):
    """Overwrite the original tracks file with only tracks without links"""
    if not tracks_without_links:
        # If no tracks left, create an empty file
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write("")
            print(f"🎉 All tracks now have links! {output_filename} is now empty.")
        except Exception as e:
            print(f"❌ Error writing to {output_filename}: {e}")
        return
    
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(tracks_without_links))
        
        print(f"📝 Updated {output_filename} with {len(tracks_without_links)} remaining tracks without links")
        
    except Exception as e:
        print(f"❌ Error writing to {output_filename}: {e}")

def update_not_found_albums(albums_without_links, output_filename="not_found_albums_again.txt"):
    """Overwrite the original albums file with only albums without links"""
    if not albums_without_links:
        # If no albums left, create an empty file
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write("")
            print(f"🎉 All albums now have links! {output_filename} is now empty.")
        except Exception as e:
            print(f"❌ Error writing to {output_filename}: {e}")
        return
    
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(albums_without_links))
        
        print(f"📝 Updated {output_filename} with {len(albums_without_links)} remaining albums without links")
        
    except Exception as e:
        print(f"❌ Error writing to {output_filename}: {e}")

def display_summary(tracks_with_links, albums_with_links):
    """Display a summary of processed tracks and albums"""
    if not tracks_with_links and not albums_with_links:
        return
    
    print("\n" + "=" * 60)
    print("📊 PROCESSED SUMMARY")
    print("=" * 60)
    
    # Count links by domain for tracks
    if tracks_with_links:
        track_domain_counts = {}
        for track in tracks_with_links:
            url = track['url']
            domain = get_domain_name(url)
            track_domain_counts[domain] = track_domain_counts.get(domain, 0) + 1
        
        print("Track links by platform:")
        for domain, count in sorted(track_domain_counts.items()):
            print(f"  🎵 {domain}: {count} tracks")
    
    # Count links by domain for albums
    if albums_with_links:
        album_domain_counts = {}
        for album in albums_with_links:
            url = album['url']
            domain = get_domain_name(url)
            album_domain_counts[domain] = album_domain_counts.get(domain, 0) + 1
        
        print("Album links by platform:")
        for domain, count in sorted(album_domain_counts.items()):
            print(f"  � {domain}: {count} albums")
    
    print(f"\n🎵 Total tracks processed: {len(tracks_with_links)}")
    print(f"💿 Total albums processed: {len(albums_with_links)}")

def get_domain_name(url):
    """Extract domain name from URL for categorization"""
    if 'tidal.com' in url:
        return 'Tidal'
    elif 'music.amazon.' in url:
        return 'Amazon Music'
    elif 'deezer.com' in url:
        return 'Deezer'
    elif 'qobuz.com' in url:
        return 'Qobuz'
    elif 'soundcloud.com' in url:
        return 'SoundCloud'
    elif 'spotify.com' in url:
        return 'Spotify'
    elif 'youtube.com' in url or 'youtu.be' in url:
        return 'YouTube'
    else:
        return 'Other'

def main():
    print("🔗 Manual Links Processor")
    print("=" * 40)
    print("This program reads manually edited files with links")
    print("and extracts links that users have added to tracks/albums.")
    print("=" * 40)
    
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
    
    tracks_with_links = []
    albums_with_links = []
    tracks_without_links = []
    albums_without_links = []
    
    # Process tracks
    if choice in ['1', '3']:
        tracks_with_links, tracks_without_links = read_manual_tracks()
    
    # Process albums
    if choice in ['2', '3']:
        albums_with_links, albums_without_links = read_manual_albums()
    
    if not tracks_with_links and not albums_with_links and not tracks_without_links and not albums_without_links:
        print("No data to process. Exiting.")
        return
    
    # Display what we found
    if tracks_with_links:
        print(f"\n✅ Found {len(tracks_with_links)} tracks with links:")
        for i, track in enumerate(tracks_with_links[:3], 1):  # Show first 3 as preview
            duration_info = f" ({track['duration']})" if track['duration'] else ""
            print(f"  {i}. {track['title']} — {track['artist']}{duration_info}")
            print(f"     🔗 {track['url']}")
        
        if len(tracks_with_links) > 3:
            print(f"     ... and {len(tracks_with_links) - 3} more")
    
    if albums_with_links:
        print(f"\n✅ Found {len(albums_with_links)} albums with links:")
        for i, album in enumerate(albums_with_links[:3], 1):  # Show first 3 as preview
            print(f"  {i}. {album['album_name']} — {album['artist']}")
            print(f"     🔗 {album['url']}")
        
        if len(albums_with_links) > 3:
            print(f"     ... and {len(albums_with_links) - 3} more")
    
    if tracks_without_links:
        print(f"\n📝 {len(tracks_without_links)} tracks still without links")
    
    if albums_without_links:
        print(f"\n📝 {len(albums_without_links)} albums still without links")
    
    # Ask for confirmation
    total_items = len(tracks_with_links) + len(albums_with_links)
    if total_items > 0:
        if choice == '1':
            print(f"\nReady to add {len(tracks_with_links)} tracks to tidal_track_links.csv")
        elif choice == '2':
            print(f"\nReady to add {len(albums_with_links)} albums to tidal_album_links.csv")
        else:
            print(f"\nReady to add {len(tracks_with_links)} tracks and {len(albums_with_links)} albums to CSV files")
        
        print(f"and update the source files with remaining items")
        try:
            confirm = input("Continue? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Operation cancelled")
                return
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return
        
        # Append to CSV files
        tracks_added = append_tracks_to_csv(tracks_with_links)
        albums_added = append_albums_to_csv(albums_with_links)
        
        # Update not found files with remaining items (overwrite originals)
        if choice in ['1', '3']:
            update_not_found_tracks(tracks_without_links)
        if choice in ['2', '3']:
            update_not_found_albums(albums_without_links)
        
        # Display summary
        if tracks_added > 0 or albums_added > 0:
            display_summary(tracks_with_links, albums_with_links)
        
        print("\n✅ Process completed successfully!")
        print("You can now use doubledouble.py to download these tracks/albums.")
        
        remaining_count = len(tracks_without_links) + len(albums_without_links)
        if remaining_count > 0:
            print(f"📝 {remaining_count} items still need links in the source files")
    else:
        print("\nNo tracks or albums with links found to process.")
        remaining_count = len(tracks_without_links) + len(albums_without_links)
        if remaining_count > 0:
            print(f"All {remaining_count} items are still missing links.")

if __name__ == "__main__":
    main()
