# Nepali Date Status Bar App

A simple macOS status bar app that displays the current Nepali date (BS/Bikram Sambat) in `YYYY-MM-DD, Day Name` format (e.g., `२०८१-०१-१३, आइतबार`) in your menu bar.

![Nepali Date Screenshot](https://i.postimg.cc/cLD0BQn3/i-Screen-Shoter-2025040564334840-AM.jpg)

## Features

- Shows the current Nepali date in `YYYY-MM-DD, Day Name` format in your macOS menu bar
- Automatically updates every 5 minutes
- Displays the date and day of week using Nepali digits and language
- Uses HamroPatro API for accurate date conversion

## Build Instructions

### Prerequisites
- macOS 10.15 or later
- Python 3.8 or later
- pip3

### Building from Source

1. Clone this repository
   ```bash
   git clone https://github.com/puskartrital/nepali_date_macos.git
   cd nepali_date_macos
   ```

2. Install dependencies
   ```bash
   pip3 install -r requirements.txt
   pip3 install pyinstaller
   ```

3. Create the icon
   ```bash
   brew install makeicns
   python3 create_icon.py
   # Or use makeicns if you have it installed
   # makeicns -in calendar.png -out calendar.icns
   ```

4. Build the app
   ```bash
   pyinstaller --name="Nepali Date" \
               --windowed \
               --noconfirm \
               --clean \
               --add-data="calendar.png:." \
               --hidden-import=rumps \
               --hidden-import=requests \
               --icon="calendar.icns" \
               nepali_date_statusbar.py
   ```

5. The app will be created in the `dist` folder. Copy it to your Applications folder:
   ```bash
   cp -r "dist/Nepali Date.app" /Applications/
   ```

6. Simply you can build and install from the script itself as well.
```
chmod +x build_with_pyinstaller.sh
./build_with_pyinstaller.sh
```
## Usage

Once installed, the app will appear in your menu bar showing the current Nepali date in the format `YYYY-MM-DD, Day Name` (e.g., `२०८१-०१-१३, आइतबार`).

The menu provides the following options:
- **Refresh**: Manually update the date
- **About**: Information about the app with a link to the GitHub repository
- **Quit**: Exit the application

## Adding to Login Items

To have the app start automatically when you log in:

1. Go to System Settings > General > Login Items
2. Click the "+" button
3. Find and select "Nepali Date.app"
4. Click "Add"

## Troubleshooting

If the app doesn't show the correct date:
- Check your internet connection (the app needs to access the HamroPatro API)
- Quit and restart the app using the menu option
- Make sure your system date and time are correct

## Privacy

This app only connects to the HamroPatro API to convert the current date. No personal data is collected or transmitted.

## Credits

- Date conversion provided by [HamroPatro](https://www.hamropatro.com/)
- Developed by [Puskar Trital](https://github.com/puskartrital)

## License

MIT License
