import pyautogui
import time
import csv

# -- Setup: optional PyAutoGUI settings --
pyautogui.PAUSE = 0.5   # pause after each PyAutoGUI call for safety
pyautogui.FAILSAFE = True  # move mouse to corner to abort

# Ask user what they want to process
print("🎵 DoubleDouble Automation Tool")
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

# Prompt user to open Brave and load the site
input("Open Brave and navigate to https://doubledouble.top. Then press Enter to start setup...")

# Capture coordinates of the input box, download button, save button by user hover
print("Hover mouse over the Tidal link input box and press Enter")
input()  # wait for user
input_box = pyautogui.position()  # get current mouse coords
print(f"Input box at {input_box}")

print("Hover mouse over the 'Download' button and press Enter")
input()
download_button = pyautogui.position()
print(f"Download button at {download_button}")

# Ask if user wants to update save button position
print("\nDo you want to set a custom Save button position? (y/N)")
update_save = input().strip().lower()
if update_save == 'y':
    print("Hover mouse over the 'Save' button and press Enter")
    input()
    save_button = pyautogui.position()
    print(f"Save button at {save_button}")
else:
    save_button = (2363, 690)  # Default position
    print(f"Using default Save button position: {save_button}")

save_button_color = (56, 56, 56)  # dark gray color in RGB

# Capture Success message location and color for detection
print("Hover mouse over the center of the green success box and press Enter")
input()
success_pos = pyautogui.position()
success_color = (29, 185, 84)  # green color in RGB
print(f"Success position at {success_pos}")

# Ask if user wants to update error position
print("\nDo you want to set a custom Error message position? (y/N)")
update_error = input().strip().lower()
if update_error == 'y':
    print("Hover mouse over the center of the red error box and press Enter")
    input()
    error_pos = pyautogui.position()
    print(f"Error position at {error_pos}")
else:
    error_pos = success_pos  # Default to same as success position
    print(f"Using default Error position (same as success): {error_pos}")

error_color = (255, 0, 0)  # red color in RGB

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



def is_save_button_visible(pos, color, tolerance=10):
    x, y = pos
    return pyautogui.pixelMatchesColor(x, y, color, tolerance=tolerance)

def is_success_visible(pos, color, tolerance=10):
    x, y = pos
    return pyautogui.pixelMatchesColor(x, y, color, tolerance=tolerance)

def is_error_visible(pos, color, tolerance=10):
    x, y = pos
    return pyautogui.pixelMatchesColor(x, y, color, tolerance=tolerance)

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
for i, link in enumerate(all_links, 1):
    # Determine if this is a track or album for logging
    link_type = "track" if link in track_links else "album"
    print(f"\n[{i}/{len(all_links)}] Processing {link_type}: {link}")
    
    # Click input box, clear any existing text, and type the new link
    pyautogui.click(input_box)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite(link, interval=0.05)
    
    link_downloaded_and_saved = False
    attempts = 0
    max_attempts = 20
    signal_timeout = 900  # seconds to wait for success or error signal

    while attempts < max_attempts:
        attempts += 1
        print(f"  Attempt {attempts}/{max_attempts}")
        pyautogui.click(download_button)
        
        current_attempt_succeeded = False
        current_attempt_failed_with_error = False
        link_ripped = False

        wait_start_time = time.time()
        while time.time() - wait_start_time < signal_timeout:
            if is_success_visible(success_pos, success_color) or link_ripped:
                print(f"  ✅ Success detected on attempt {attempts}")
                link_ripped = True
                # click save button when you see save message
                if is_save_button_visible(save_button, save_button_color):
                    pyautogui.click(save_button)
                    print(f"  💾 Save button clicked")
                    link_downloaded_and_saved = True
                    current_attempt_succeeded = True
                    break  # from inner signal_wait_loop
            
            if is_error_visible(error_pos, error_color):
                print(f"  ❌ Error detected on attempt {attempts}")
                current_attempt_failed_with_error = True
                break  # from inner signal_wait_loop
            
            time.sleep(0.5)  # Poll every half second

        if current_attempt_succeeded:
            break  # from attempts loop, this link is done

        if current_attempt_failed_with_error:
            if attempts < max_attempts:
                print("  🔄 Retrying...")
                time.sleep(1)  # Brief pause before retrying
            else:
                print(f"  ⚠️  Max attempts reached due to persistent error")
            if attempts >= max_attempts:
                break 
            else:
                continue
        
        # If neither success nor error was visible (timeout of inner loop)
        if not current_attempt_succeeded and not current_attempt_failed_with_error:
            print(f"  ⏱️  Timeout waiting for response on attempt {attempts}")
            if attempts < max_attempts:
                print("  🔄 Retrying...")
                time.sleep(1)
            else:
                print(f"  ⚠️  Max attempts reached due to persistent timeout")
            if attempts >= max_attempts:
                break
            else:
                continue

    if link_downloaded_and_saved:
        print(f"  ✅ Successfully processed: {link}")
        time.sleep(1)  # Wait for download to complete
    else:
        print(f"  ❌ Failed after {max_attempts} attempts: {link}")
        failed_links.append(link)

# Save failed links to file
if failed_links:
    filename = "not_downloaded_tracks.txt" if choice == '1' else \
               "not_downloaded_albums.txt" if choice == '2' else \
               "not_downloaded_links.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(failed_links))
    print(f"\n📝 {len(failed_links)} failed links saved to {filename}")

print(f"\n🎉 Processing completed!")
print(f"   Total processed: {len(all_links)}")
print(f"   Successful: {len(all_links) - len(failed_links)}")
print(f"   Failed: {len(failed_links)}")
