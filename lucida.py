import pyautogui
import time
import csv

# -- Setup: optional PyAutoGUI settings --
pyautogui.PAUSE = 0.5   # pause after each PyAutoGUI call for safety
pyautogui.FAILSAFE = True  # move mouse to corner to abort

# Ask user what they want to process
print("🎵 Lucida Automation Tool")
print("=" * 40)
print("What would you like to download?")
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
        exit()

# Prompt user to open browser and load the site
input("Open your browser and navigate to lucida.to or lucida.su. Then press Enter to start setup...")

# Capture coordinates of the input box, download button, and other elements by user hover
print("Hover mouse over the Tidal link input box and press Enter")
input()  # wait for user
input_box = pyautogui.position()  # get current mouse coords
print(f"Input box at {input_box}")

print("Hover mouse over the 'Download' or 'Submit' button and press Enter")
input()
download_button = pyautogui.position()
print(f"Download button at {download_button}")

# Ask if user wants to update download link position
print("\nDo you want to set a custom Download link position? (y/N)")
update_download_link = input().strip().lower()
if update_download_link == 'y':
    print("Hover mouse over the download link that appears after processing and press Enter")
    input()
    download_link_pos = pyautogui.position()
    print(f"Download link at {download_link_pos}")
else:
    download_link_pos = (960, 500)  # Default position (center-ish)
    print(f"Using default download link position: {download_link_pos}")

# Capture Success message location and color for detection
print("Hover mouse over the area where success messages appear and press Enter")
input()
success_pos = pyautogui.position()
success_color = (34, 197, 94)  # green color in RGB (adjust as needed)
print(f"Success position at {success_pos}")

# Ask if user wants to update error position
print("\nDo you want to set a custom Error message position? (y/N)")
update_error = input().strip().lower()
if update_error == 'y':
    print("Hover mouse over the area where error messages appear and press Enter")
    input()
    error_pos = pyautogui.position()
    print(f"Error position at {error_pos}")
else:
    error_pos = success_pos  # Default to same as success position
    print(f"Using default Error position (same as success): {error_pos}")

error_color = (239, 68, 68)  # red color in RGB (adjust as needed)

# Load links from files based on user choice
def load_track_links(filename="tidal_track_links.csv"):
    """Load Tidal track URLs from CSV file"""
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            links = [row['Tidal URL'].strip() for row in reader if row.get('Tidal URL')]
        return links
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []
    except KeyError:
        print(f"Error: 'Tidal URL' column not found in {filename}.")
        return []
    except Exception as e:
        print(f"Error loading links from {filename}: {e}")
        return []

def load_album_links(filename="tidal_album_links.csv"):
    """Load Tidal album URLs from CSV file"""
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            links = [row['Tidal URL'].strip() for row in reader if row.get('Tidal URL')]
        return links
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []
    except KeyError:
        print(f"Error: 'Tidal URL' column not found in {filename}.")
        return []
    except Exception as e:
        print(f"Error loading links from {filename}: {e}")
        return []

# Load links based on user choice
track_links = []
album_links = []
all_links = []

if choice in ['1', '3']:  # Tracks only or both
    track_links = load_track_links()
    all_links.extend(track_links)
    
if choice in ['2', '3']:  # Albums only or both
    album_links = load_album_links()
    all_links.extend(album_links)

# Display summary
if choice == '1':
    print(f"Loaded {len(track_links)} track links for processing")
elif choice == '2':
    print(f"Loaded {len(album_links)} album links for processing")
else:
    print(f"Loaded {len(track_links)} track links and {len(album_links)} album links")
    print(f"Total: {len(all_links)} links for processing")

def is_download_link_visible(pos, tolerance=50):
    """Check if download link is visible by looking for text or color changes"""
    x, y = pos
    # This is a simple check - you may need to adjust based on actual site behavior
    return True  # Placeholder - implement actual detection logic

def is_success_visible(pos, color, tolerance=20):
    x, y = pos
    return pyautogui.pixelMatchesColor(x, y, color, tolerance=tolerance)

def is_error_visible(pos, color, tolerance=20):
    x, y = pos
    return pyautogui.pixelMatchesColor(x, y, color, tolerance=tolerance)

def wait_for_processing_complete(timeout=120):
    """Wait for processing to complete on Lucida"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Check for success indicators
        if is_success_visible(success_pos, success_color):
            return "success"
        
        # Check for error indicators
        if is_error_visible(error_pos, error_color):
            return "error"
        
        # Look for download link appearance
        if is_download_link_visible(download_link_pos):
            return "download_ready"
        
        time.sleep(1)
    
    return "timeout"

# Check if links were loaded successfully
if not all_links:
    if choice == '1':
        print("No track links found. Please run get_tidal_links.py or manual_get_tidal_links.py first.")
    elif choice == '2':
        print("No album links found. Please run get_tidal_links.py or manual_get_tidal_links.py first.")
    else:
        print("No track or album links found. Please run get_tidal_links.py or manual_get_tidal_links.py first.")
    input("Press Enter to exit...")
    exit()

print("Starting automation of links...")

# Process links with progress tracking
failed_links = []
successful_links = []

for i, link in enumerate(all_links, 1):
    # Determine if this is a track or album for logging
    link_type = "track" if link in track_links else "album"
    print(f"\n[{i}/{len(all_links)}] Processing {link_type}: {link}")
    
    # Click input box, clear any existing text, and type the new link
    pyautogui.click(input_box)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite(link, interval=0.05)
    
    link_processed_successfully = False
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts and not link_processed_successfully:
        attempts += 1
        print(f"  Attempt {attempts}/{max_attempts}")
        
        # Click download/submit button
        pyautogui.click(download_button)
        
        # Wait for processing to complete
        result = wait_for_processing_complete()
        
        if result == "success" or result == "download_ready":
            print(f"  ✅ Processing completed successfully on attempt {attempts}")
            
            # Click on download link if it's available
            if is_download_link_visible(download_link_pos):
                pyautogui.click(download_link_pos)
                print(f"  💾 Download link clicked")
                time.sleep(2)  # Give time for download to start
            
            link_processed_successfully = True
            successful_links.append(link)
            
        elif result == "error":
            print(f"  ❌ Error detected on attempt {attempts}")
            if attempts < max_attempts:
                print("  🔄 Retrying...")
                time.sleep(2)  # Wait before retry
            
        elif result == "timeout":
            print(f"  ⏱️  Timeout waiting for processing on attempt {attempts}")
            if attempts < max_attempts:
                print("  🔄 Retrying...")
                time.sleep(2)  # Wait before retry

    if not link_processed_successfully:
        print(f"  ❌ Failed after {max_attempts} attempts: {link}")
        failed_links.append(link)
    
    # Small delay between links
    time.sleep(1)

# Save failed links to file
if failed_links:
    filename = "lucida_not_downloaded_tracks.txt" if choice == '1' else \
               "lucida_not_downloaded_albums.txt" if choice == '2' else \
               "lucida_not_downloaded_links.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(failed_links))
    print(f"\n📝 {len(failed_links)} failed links saved to {filename}")

print(f"\n🎉 Processing completed!")
print(f"   Total processed: {len(all_links)}")
print(f"   Successful: {len(successful_links)}")
print(f"   Failed: {len(failed_links)}")