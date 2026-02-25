#!/usr/bin/env python3
"""
Convert GeoTIFF or TIFF files to formats optimized for Gazebo.
Handles georeferenced imagery and converts to PNG/JPG for best compatibility.
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Install with: pip3 install pillow numpy")
    sys.exit(1)

def convert_tiff(input_path, output_path=None, output_format='PNG', max_size=4096):
    """
    Convert TIFF to PNG/JPG for Gazebo
    
    Args:
        input_path: Path to input TIFF file
        output_path: Path to output file (optional)
        output_format: 'PNG' or 'JPEG'
        max_size: Maximum dimension (will resize if larger)
    """
    
    print(f"Loading TIFF file: {input_path}")
    
    # Try to open with GDAL first (for GeoTIFF)
    try:
        from osgeo import gdal
        gdal.UseExceptions()
        
        ds = gdal.Open(input_path)
        if ds is not None:
            print(f"✓ Detected GeoTIFF with {ds.RasterCount} bands")
            
            # Read bands
            bands = []
            for i in range(1, min(4, ds.RasterCount + 1)):  # RGB or RGBA
                band = ds.GetRasterBand(i)
                data = band.ReadAsArray()
                bands.append(data)
            
            # Stack bands
            if len(bands) == 1:
                img_array = bands[0]
            else:
                img_array = np.stack(bands, axis=-1)
            
            # Normalize to 0-255 if needed
            if img_array.dtype != np.uint8:
                img_array = ((img_array - img_array.min()) / 
                            (img_array.max() - img_array.min()) * 255).astype(np.uint8)
            
            img = Image.fromarray(img_array)
            print(f"✓ Loaded GeoTIFF: {img.size[0]}x{img.size[1]} pixels")
            
    except ImportError:
        print("  GDAL not installed, trying PIL...")
        img = None
    except Exception as e:
        print(f"  GDAL failed: {e}, trying PIL...")
        img = None
    
    # Fallback to PIL
    if img is None:
        img = Image.open(input_path)
        print(f"✓ Loaded TIFF: {img.size[0]}x{img.size[1]} pixels, mode: {img.mode}")
    
    # Convert to RGB if needed
    if img.mode not in ('RGB', 'RGBA', 'L'):
        print(f"  Converting from {img.mode} to RGB...")
        img = img.convert('RGB')
    
    # Resize if too large
    width, height = img.size
    if max(width, height) > max_size:
        ratio = max_size / max(width, height)
        new_size = (int(width * ratio), int(height * ratio))
        print(f"  Resizing from {width}x{height} to {new_size[0]}x{new_size[1]}...")
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Set output path
    if output_path is None:
        input_file = Path(input_path)
        ext = '.png' if output_format == 'PNG' else '.jpg'
        output_path = input_file.parent / f"{input_file.stem}_gazebo{ext}"
    
    # Save
    print(f"Saving as {output_format}: {output_path}")
    if output_format == 'JPEG':
        img = img.convert('RGB')  # JPEG doesn't support alpha
        img.save(output_path, 'JPEG', quality=95)
    else:
        img.save(output_path, 'PNG', optimize=True)
    
    print(f"✓ Conversion complete!")
    print(f"  Output: {output_path}")
    print(f"  Size: {img.size[0]}x{img.size[1]} pixels")
    
    return str(output_path)

def link_to_gazebo_world(texture_path):
    """Update the world file to use the new texture"""
    world_file = Path.home() / "ardu_ws/src/ardupilot_gz/ardupilot_gz_gazebo/worlds/iris_heightmap.sdf"
    
    if not world_file.exists():
        print(f"\nWorld file not found: {world_file}")
        return
    
    print(f"\nTo use this texture in Gazebo:")
    print(f"1. Edit: {world_file}")
    print(f"2. Update the albedo_map line to:")
    print(f"   <albedo_map>file://{texture_path}</albedo_map>")
    print(f"\nOr run:")
    print(f"  sed -i 's|<albedo_map>.*</albedo_map>|<albedo_map>file://{texture_path}</albedo_map>|' {world_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 convert_tiff_to_gazebo.py <input.tif> [output.png] [format]")
        print("\nExamples:")
        print("  python3 convert_tiff_to_gazebo.py satellite.tif")
        print("  python3 convert_tiff_to_gazebo.py satellite.tif output.png PNG")
        print("  python3 convert_tiff_to_gazebo.py satellite.tif output.jpg JPEG")
        print("\nSupported formats: PNG (default), JPEG")
        print("\nNote: Install GDAL for better GeoTIFF support:")
        print("  sudo apt install python3-gdal")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    output_format = sys.argv[3].upper() if len(sys.argv) > 3 else 'PNG'
    
    if not os.path.exists(input_path):
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)
    
    if output_format not in ('PNG', 'JPEG'):
        print(f"ERROR: Invalid format '{output_format}'. Use PNG or JPEG")
        sys.exit(1)
    
    print("=" * 60)
    print("TIFF to Gazebo Converter")
    print("=" * 60)
    
    try:
        output = convert_tiff(input_path, output_path, output_format)
        link_to_gazebo_world(output)
        
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
