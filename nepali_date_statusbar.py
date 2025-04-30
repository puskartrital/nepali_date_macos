#!/usr/bin/env python3
import rumps
from datetime import datetime
import threading
import time
import os
import requests
import re
import sys
import webbrowser

class NepaliDateStatusBarApp(rumps.App):
    def __init__(self):
        # Get the icon path - handle both running as script and as bundled app
        if getattr(sys, 'frozen', False):
            # We're running in a bundle
            bundle_dir = os.path.dirname(sys.executable)
            # Try to find both PNG and ICNS
            icon_path = os.path.join(bundle_dir, 'calendar.icns')
            if not os.path.exists(icon_path):
                icon_path = os.path.join(bundle_dir, 'calendar.png')
        else:
            # We're running in a normal Python environment
            # Try ICNS first, then fall back to PNG
            icon_path = "calendar.icns" if os.path.exists("calendar.icns") else "calendar.png"
        
        icon = icon_path if os.path.exists(icon_path) else None
        if not icon:
            print(f"Warning: Icon not found at {icon_path}")
        
        # Important: When setting quit_button to None, we need to ensure
        # we have our own menu handler to quit the app
        super(NepaliDateStatusBarApp, self).__init__("", icon=icon, quit_button=None)
        self.menu = ["Refresh", "About", rumps.separator, "Quit"]
        # Update the date initially
        self.update_date()
        # Start a background thread to update the date every 5 minutes
        self.start_update_thread()

    def get_nepali_date_from_hamropatro(self):
        """
        Get the raw Nepali date string from HamroPatro API
        Returns the date string (e.g., "२०८१ बैशाख १") or None if failed
        """
        try:
            today = datetime.now()
            date_str = today.strftime('%Y-%m-%d')
            print(f"Requesting Nepali date for English date: {date_str}")

            payload = {
                'actionName': 'wdconverter',
                'datefield': date_str,
                'convert_option': 'eng_to_nep'
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            api_url = 'https://www.hamropatro.com/getMethod.php'

            response = requests.post(api_url, data=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                response_text = response.text.strip()
                print(f"HamroPatro API raw response: '{response_text}'")

                # Extract content inside <span> tags
                span_pattern = r'<span>(.*?)</span>'
                span_match = re.search(span_pattern, response_text)

                if span_match:
                    nepali_date_str = span_match.group(1).strip() # e.g., "२०८१ बैशाख १"
                    print(f"Extracted raw Nepali date string: '{nepali_date_str}'")
                    # Return the raw string directly
                    return nepali_date_str
                else:
                    print(f"Error: Could not find date span (<span>...</span>) in API response: '{response_text}'")
                    return None # Indicate failure
            else:
                 print(f"Error: HamroPatro API returned status code {response.status_code}. Response: '{response_text}'")
                 return None # Indicate failure

        except requests.exceptions.Timeout:
            print("Error: Request to HamroPatro API timed out.")
            return None # Indicate failure
        except requests.exceptions.RequestException as e:
            print(f"Error during request to HamroPatro API: {e}")
            return None # Indicate failure
        except Exception as e:
            print(f"Unexpected error in get_nepali_date_from_hamropatro: {e}")
            return None # Indicate failure

    def update_date(self):
        try:
            # Get raw date string from HamroPatro API
            raw_date_string = self.get_nepali_date_from_hamropatro()

            if raw_date_string is not None:
                # Directly use the raw string from the API
                self.title = raw_date_string
                print(f"Updated status bar title to: '{raw_date_string}'")
            else:
                # Handle failure to get the date string
                print("Failed to get date string from HamroPatro API")
                self.title = "मिति अनुपलब्ध"  # "Date Unavailable" in Nepali

        except Exception as e:
            # Catch errors within update_date itself (less likely now)
            print(f"Error updating date: {e}")
            self.title = "त्रुटि" # "Error" in Nepali

    def start_update_thread(self):
        # Create and start a background thread for updating the date
        update_thread = threading.Thread(target=self.update_periodically)
        update_thread.daemon = True
        update_thread.start()
    
    def update_periodically(self):
        while True:
            # Update every 5 minutes (300 seconds)
            time.sleep(300)
            # Silent update without notification for cleaner experience
            self.update_date()
    
    @rumps.clicked("Refresh")
    def refresh(self, _):
        print("Manually refreshing date...")
        self.update_date()
    
    @rumps.clicked("About")
    def about(self, _):
        # Show About dialog with a button to open GitHub repo
        response = rumps.alert(
            title="Nepali Date",
            message="Displays current Nepali date in the status bar.\n\nVisit GitHub Repository?",
            ok="Open GitHub",
            cancel="Close"
        )
        if response == 1:  # User clicked "Open GitHub"
            webbrowser.open("https://github.com/puskartrital/nepali_date_macos")
    
    @rumps.clicked("Quit")
    def quit(self, _):
        rumps.quit_application()

if __name__ == '__main__':
    print("Starting Nepali Date Status Bar App...")
    NepaliDateStatusBarApp().run()
