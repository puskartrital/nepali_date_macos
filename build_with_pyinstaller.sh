#!/bin/bash

echo "Building Nepali Date Status Bar App with PyInstaller..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (removed Pillow since not needed)
pip3 install --upgrade pip
pip3 install rumps==0.4.0
pip3 install pyobjc-framework-Cocoa==9.2
pip3 install requests==2.31.0
pip3 install pyinstaller

# Verify icons exist
if [ ! -f "calendar.png" ]; then
    echo "Warning: PNG icon not found."
fi

if [ ! -f "calendar.icns" ]; then
    echo "Warning: ICNS icon not found."
    if [ -f "calendar.png" ]; then
        echo "Generating ICNS from PNG using makeicns..."
        makeicns -in calendar.png -out calendar.icns || echo "Failed to create ICNS icon"
    fi
fi

# Clean previous builds
rm -rf dist build

# Build the app with PyInstaller
echo "Running PyInstaller..."
pyinstaller --name="Nepali Date" \
            --windowed \
            --noconfirm \
            --clean \
            --add-data="calendar.png:." \
            --hidden-import=rumps \
            --hidden-import=requests \
            --icon="calendar.icns" \
            nepali_date_statusbar.py

# Check if build was successful
if [ -d "dist/Nepali Date.app" ]; then
    echo "✅ Build successful! App is in dist/Nepali Date.app"
    
    # Copy the icons to ensure they're available
    if [ -f "calendar.png" ]; then
        mkdir -p "dist/Nepali Date.app/Contents/Resources"
        cp calendar.png "dist/Nepali Date.app/Contents/Resources/"
    fi
    
    if [ -f "calendar.icns" ]; then
        mkdir -p "dist/Nepali Date.app/Contents/Resources"
        cp calendar.icns "dist/Nepali Date.app/Contents/Resources/"
        # Also copy it to where PyInstaller expects it
        cp calendar.icns "dist/Nepali Date.app/Contents/Resources/icon-windowed.icns"
    fi
    
    echo "✓ Icons copied to app bundle"
    
    # Optional: Copy to Applications folder
    read -p "Would you like to install the app to your Applications folder? (y/n) " choice
    if [[ $choice == "y" || $choice == "Y" ]]; then
        cp -r "dist/Nepali Date.app" "/Applications/"
        echo "✓ App installed to Applications folder"
    fi
    
    # Optional: Run the app
    read -p "Would you like to run the app now? (y/n) " choice
    if [[ $choice == "y" || $choice == "Y" ]]; then
        open "dist/Nepali Date.app"
    fi
else
    echo "❌ Build failed. Check the errors above."
fi

# Deactivate virtual environment
deactivate

echo "Done!"
