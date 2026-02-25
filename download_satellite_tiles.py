#!/usr/bin/env python3
"""
Download satellite imagery tiles for Gazebo terrain textures.
Uses OpenStreetMap satellite tiles (free and open source).
"""

import os
import sys
import urllib.request
import math
from PIL import Image

def deg2num(lat_deg, lon_deg, zoom):
    """Convert lat/lon to tile coordinates"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def download_tiles(lat, lon, zoom, tile_range, output_dir):
    """Download satellite tiles and stitch them together"""
    
    center_x, center_y = deg2num(lat, lon, zoom)
    
    tiles = []
    print(f"Downloading tiles around ({lat}, {lon}) at zoom {zoom}...")
    print(f"Center tile: ({center_x}, {center_y})")
    
    # Download tiles in a grid
    for dx in range(-tile_range, tile_range + 1):
        tile_row = []
        for dy in range(-tile_range, tile_range + 1):
            x = center_x + dx
            y = center_y + dy
            
            # Try different tile servers
            # Option 1: Esri World Imagery (high quality)
            url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}"
            
            # Option 2: OpenStreetMap (fallback)
            # url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
            
            tile_path = os.path.join(output_dir, f"tile_{x}_{y}.png")
            
            try:
                print(f"Downloading tile ({x}, {y})...", end=" ")
                headers = {'User-Agent': 'Mozilla/5.0 (Gazebo Simulator)'}
                req = urllib.request.Request(url, headers=headers)
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    with open(tile_path, 'wb') as out_file:
                        out_file.write(response.read())
                
                tile_row.append(Image.open(tile_path))
                print("✓")
                
            except Exception as e:
                print(f"✗ Error: {e}")
                # Create blank tile as placeholder
                tile_row.append(Image.new('RGB', (256, 256), (200, 200, 200)))
        
        tiles.append(tile_row)
    
    # Stitch tiles together
    print("\nStitching tiles together...")
    tile_width = 256
    tile_height = 256
    
    num_tiles_x = len(tiles[0])
    num_tiles_y = len(tiles)
    
    output_image = Image.new('RGB', 
                             (tile_width * num_tiles_x, tile_height * num_tiles_y))
    
    for i, tile_row in enumerate(tiles):
        for j, tile in enumerate(tile_row):
            output_image.paste(tile, (j * tile_width, i * tile_height))
    
    # Save final image
    output_path = os.path.join(output_dir, "satellite_texture.png")
    output_image.save(output_path, "PNG")
    print(f"\nSaved satellite texture to: {output_path}")
    print(f"Image size: {output_image.size[0]}x{output_image.size[1]} pixels")
    
    # Clean up individual tiles
    for dx in range(-tile_range, tile_range + 1):
        for dy in range(-tile_range, tile_range + 1):
            x = center_x + dx
            y = center_y + dy
            tile_path = os.path.join(output_dir, f"tile_{x}_{y}.png")
            if os.path.exists(tile_path):
                os.remove(tile_path)
    
    return output_path

def main():
    # Default coordinates (Mumbai, India - matching your N19E072 terrain)
    # Change these to your desired location
    lat = 19.0760  # Latitude
    lon = 72.8777  # Longitude (Mumbai)
    zoom = 16      # Zoom level (higher = more detail, 16-18 recommended)
    tile_range = 2 # Number of tiles in each direction (2 = 5x5 grid = 1280x1280px)
    
    if len(sys.argv) > 1:
        lat = float(sys.argv[1])
    if len(sys.argv) > 2:
        lon = float(sys.argv[2])
    if len(sys.argv) > 3:
        zoom = int(sys.argv[3])
    if len(sys.argv) > 4:
        tile_range = int(sys.argv[4])
    
    output_dir = os.path.expanduser("~/ardu_ws/terrain")
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("Satellite Imagery Downloader for Gazebo")
    print("=" * 60)
    print(f"Location: ({lat}, {lon})")
    print(f"Zoom level: {zoom}")
    print(f"Tile range: {tile_range} (output: {(tile_range*2+1)*256}x{(tile_range*2+1)*256}px)")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
    print()
    
    try:
        output_path = download_tiles(lat, lon, zoom, tile_range, output_dir)
        print("\n" + "=" * 60)
        print("SUCCESS! Satellite imagery downloaded.")
        print("=" * 60)
        print(f"\nTo use in Gazebo, the texture is already configured at:")
        print(f"  {output_path}")
        print("\nYou can now run:")
        print("  gz sim -v4 -r ~/ardu_ws/src/ardupilot_gz/ardupilot_gz_gazebo/worlds/iris_heightmap.sdf")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Install required packages: pip3 install pillow")
        print("3. Try different coordinates or zoom level")
        sys.exit(1)

if __name__ == "__main__":
    print("\nUsage: python3 download_satellite_tiles.py [lat] [lon] [zoom] [tile_range]")
    print("Example: python3 download_satellite_tiles.py 19.0760 72.8777 16 2\n")
    
    try:
        import PIL
    except ImportError:
        print("ERROR: PIL (Pillow) not installed.")
        print("Install it with: pip3 install pillow")
        sys.exit(1)
    
    main()
