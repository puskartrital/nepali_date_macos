#!/usr/bin/env python3
from PIL import Image, ImageDraw
import os
import sys
import tempfile
import subprocess

def create_calendar_icon(output_file="calendar.png", size=(1024, 1024)):
    """Create a minimal, clean calendar icon and save it to the specified output file."""
    try:
        # Create a new image with transparent background
        img = Image.new('RGBA', size, color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simpler, more minimal calendar icon
        margin = int(size[0] * 0.1)
        width = size[0] - 2 * margin
        height = size[1] - 2 * margin
        x_start = margin
        y_start = margin
        
        # Calendar base (rounded rectangle)
        draw.rounded_rectangle(
            [x_start, y_start, x_start + width, y_start + height],
            radius=int(width * 0.1),
            fill=(255, 255, 255, 230),
            outline=(80, 80, 80, 255),
            width=10
        )
        
        # Calendar header
        header_height = int(height * 0.25)
        draw.rounded_rectangle(
            [x_start, y_start, x_start + width, y_start + header_height],
            radius=int(width * 0.1),
            fill=(220, 50, 50, 230),
            outline=None
        )
        
        # Calendar page lines (very minimal, just 2 lines)
        line_y1 = y_start + header_height + int(height * 0.25)
        line_y2 = y_start + header_height + int(height * 0.5)
        
        line_width = 5
        draw.line(
            [x_start + int(width * 0.15), line_y1, x_start + width - int(width * 0.15), line_y1],
            fill=(150, 150, 150, 180),
            width=line_width
        )
        
        draw.line(
            [x_start + int(width * 0.15), line_y2, x_start + width - int(width * 0.15), line_y2],
            fill=(150, 150, 150, 180),
            width=line_width
        )
        
        # Make the icon work well in dark mode
        img.save(output_file)
        icon_path = os.path.abspath(output_file)
        print(f"Calendar PNG icon created at: {icon_path}")
        return icon_path
    except Exception as e:
        print(f"Error creating icon: {e}")
        return None

def create_icns_from_png(png_path, icns_path="calendar.icns"):
    """Convert a PNG file to ICNS format for macOS."""
    try:
        print(f"Converting {png_path} to {icns_path}...")
        
        # Method 1: Using iconutil (macOS specific)
        # Create temporary iconset directory
        with tempfile.TemporaryDirectory() as iconset_dir:
            iconset_path = f"{iconset_dir}/icon.iconset"
            os.makedirs(iconset_path, exist_ok=True)
            
            # Load the original image
            original = Image.open(png_path)
            
            # Create various icon sizes
            icon_sizes = [16, 32, 64, 128, 256, 512, 1024]
            
            for size in icon_sizes:
                # Regular size
                resized = original.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(f"{iconset_path}/icon_{size}x{size}.png")
                
                # @2x size (high resolution)
                if size * 2 <= 1024:  # Don't exceed 1024
                    resized = original.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
                    resized.save(f"{iconset_path}/icon_{size}x{size}@2x.png")
            
            # Convert iconset to icns using iconutil
            result = subprocess.run(
                ["iconutil", "-c", "icns", iconset_path, "-o", icns_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Error converting to ICNS: {result.stderr}")
                return None
                
            print(f"ICNS icon created at: {os.path.abspath(icns_path)}")
            return os.path.abspath(icns_path)
                
    except Exception as e:
        print(f"Error creating ICNS: {e}")
        return None

if __name__ == "__main__":
    # Create PNG icon first
    png_path = create_calendar_icon()
    
    # Then convert to ICNS
    if png_path:
        icns_path = create_icns_from_png(png_path)
        if (icns_path):
            print(f"Successfully created ICNS icon: {icns_path}")
        else:
            print("Failed to create ICNS icon")
    else:
        print("Failed to create PNG icon")
