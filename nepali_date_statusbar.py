#!/usr/bin/env python3
import rumps
from datetime import datetime
import threading
import time
import os
import sys
import webbrowser
from nepali_datetime import date as nepali_date

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

    def get_nepali_date_local(self):
        """
        Get Nepali date using nepali-datetime library (no network required)
        Returns the full Nepali date string with day name
        Format: "१४ पुष २०८१, सोमबार"
        """
        try:
            # Get today's Nepali date using the library
            today_nepali = nepali_date.today()
            
            # Get day of week from English date
            eng_weekday = datetime.now().weekday()
            day_name = self.get_nepali_day_name(eng_weekday)
            
            # Get month name
            month_name = self.get_nepali_month_name(today_nepali.month)
            
            # Convert day and year to Nepali digits
            day_num = self.convert_english_to_nepali_digits(today_nepali.day)
            year_num = self.convert_english_to_nepali_digits(today_nepali.year)
            
            # Format: "१४ पुष २०८१, सोमबार" (same format as onlinekhabar)
            formatted_date = f"{day_num} {month_name} {year_num}, {day_name}"
            
            print(f"Nepali date calculated: {formatted_date}")
            return formatted_date
            
        except Exception as e:
            print(f"Error calculating Nepali date: {e}")
            return None
    
    def update_date(self):
        try:
            # Get date using nepali-datetime library (no network required)
            nepali_date_str = self.get_nepali_date_local()
            
            if nepali_date_str:
                # Format: "१४ पुष २०८१, सोमबार"
                print(f"Debug - Nepali date: '{nepali_date_str}'")
                
                # Update the title in status bar
                self.title = nepali_date_str
            else:
                print("Failed to calculate Nepali date")
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