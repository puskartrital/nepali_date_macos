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
    
    def get_nepali_month_name(self, month_num):
        """Return Nepali month name for the given month number (1-12)"""
        nepali_months = [
            "बैशाख", "जेठ", "असार", "श्रावण", 
            "भदौ", "असोज", "कार्तिक", "मंसिर", 
            "पुष", "माघ", "फाल्गुन", "चैत्र"
        ]
        # Ensure month_num is within valid range
        if month_num < 1 or month_num > 12:
            print(f"Warning: Invalid month number {month_num}, defaulting to Baishakh")
            return nepali_months[0]
        return nepali_months[month_num - 1]
    
    def get_nepali_day_name(self, day_of_week):
        """Return full Nepali day name for the given day number (0-6, where 0 is Monday)"""
        nepali_days = [
            "सोमबार", "मंगलबार", "बुधबार", 
            "बिहिबार", "शुक्रबार", "शनिबार", "आइतबार"
        ]
        # Ensure day_of_week is within valid range (0-6)
        day_index = day_of_week % 7
        return nepali_days[day_index]
    
    def convert_english_to_nepali_digits(self, number):
        """Convert English digits to Nepali digits"""
        nepali_digits = ['०', '१', '२', '३', '४', '५', '६', '७', '८', '९']
        nepali_number = ""
        for digit in str(number):
            if digit.isdigit():
                nepali_number += nepali_digits[int(digit)]
            else:
                nepali_number += digit
        return nepali_number

    def get_nepali_date_from_hamropatro(self):
        """
        Get Nepali date from HamroPatro API
        Returns a tuple of (year, month, day) or None if failed
        """
        try:
            today = datetime.now()
            date_str = today.strftime('%Y-%m-%d')
            
            # Make a POST request to HamroPatro API
            response = requests.post(
                'https://www.hamropatro.com/getMethod.php',
                data={
                    'actionName': 'wdconverter',
                    'datefield': date_str,
                    'convert_option': 'eng_to_nep'
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                },
                timeout=5  # 5 seconds timeout
            )
            
            if response.status_code == 200:
                response_text = response.text.strip()
                print(f"HamroPatro API response: {response_text}")
                
                # Extract content inside <span> tags
                span_pattern = r'<span>(.*?)</span>'
                span_match = re.search(span_pattern, response_text)
                
                if span_match:
                    nepali_date_str = span_match.group(1)  # "२०८१ चैत २२"
                    print(f"Extracted Nepali date: {nepali_date_str}")
                    
                    # Split the date parts - format is "year month day"
                    parts = nepali_date_str.split()
                    if len(parts) >= 3:
                        year_str = parts[0]  # "२०८१"
                        month_str = parts[1]  # "चैत"
                        day_str = parts[2]  # "२२"
                        
                        # Convert Nepali digits to English
                        nepali_to_english = {
                            '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
                            '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
                        }
                        
                        try:
                            day = int(''.join([nepali_to_english.get(c, c) for c in day_str]))
                            year = int(''.join([nepali_to_english.get(c, c) for c in year_str]))
                            
                            # Convert Nepali month name to month number
                            nepali_month_names = [
                                "बैशाख", "जेठ", "असार", "श्रावण", 
                                "भदौ", "असोज", "कार्तिक", "मंसिर", 
                                "पुष", "माघ", "फाल्गुन", "चैत्र"
                            ]
                            
                            # Try to match month name
                            month = None
                            for i, m_name in enumerate(nepali_month_names):
                                if month_str == m_name:
                                    month = i + 1
                                    break
                            
                            # If month wasn't found by exact match, try partial match
                            if month is None:
                                for i, m_name in enumerate(nepali_month_names):
                                    if m_name in month_str or month_str in m_name:
                                        month = i + 1
                                        break
                            
                            # If still not found, fallback to Chaitra (month 12) as last resort
                            if month is None:
                                print(f"Could not identify month '{month_str}', defaulting to Chaitra (12)")
                                month = 12
                            
                            print(f"Parsed Nepali date: Year={year}, Month={month}, Day={day}")
                            return (year, month, day)
                        except Exception as e:
                            print(f"Error parsing date parts: {e}")
                            return None
            
            return None
        except Exception as e:
            print(f"Error fetching date from HamroPatro API: {e}")
            return None
    
    def update_date(self):
        try:
            # Get date from HamroPatro API
            date_data = self.get_nepali_date_from_hamropatro()
            
            if date_data:
                year, month, day = date_data
                
                # Print debug info
                print(f"Debug - Nepali date: Year={year}, Month={month}, Day={day}")
                
                # Get Nepali month name and day name
                month_name = self.get_nepali_month_name(month)
                
                # For the day name, use the English weekday as a reference
                eng_now = datetime.now()
                eng_weekday = eng_now.weekday()
                day_name = self.get_nepali_day_name(eng_weekday)
                
                # Convert digits to Nepali
                nepali_day = self.convert_english_to_nepali_digits(day)
                nepali_year = self.convert_english_to_nepali_digits(year)
                
                # Format date with Nepali month name and full day name
                formatted_date = f"{nepali_day} {month_name} {nepali_year}, {day_name}"
                
                print(f"Debug - Formatted date: {formatted_date}")
                
                # Update the title in status bar
                self.title = formatted_date
            else:
                print("Failed to get date from HamroPatro API")
                self.title = "दिना: अनुपलब्ध"  # "Date: Unavailable" in Nepali
                
        except Exception as e:
            print(f"Error updating date: {e}")
            self.title = "Error: Could not update date"
    
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
