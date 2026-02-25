#!/bin/bash

# Script to download satellite imagery for Gazebo terrain textures
# You'll need to install these tools first:
# sudo apt install gdal-bin python3-gdal

echo "Satellite Texture Download Options:"
echo ""
echo "1. OpenStreetMap Tiles:"
echo "   - Free and open source"
echo "   - Visit: https://www.openstreetmap.org"
echo "   - Export area and save as PNG"
echo ""
echo "2. Google Earth Engine (requires account):"
echo "   - High resolution imagery"
echo "   - Visit: https://earthengine.google.com"
echo ""
echo "3. USGS Earth Explorer:"
echo "   - Landsat/Sentinel data"
echo "   - Visit: https://earthexplorer.usgs.gov"
echo ""
echo "4. Using gdal2tiles (for existing GeoTIFF):"
echo "   gdal2tiles.py -z 10-15 input.tif output/"
echo ""
echo "5. Manual screenshot from Google Maps:"
echo "   - Open maps.google.com"
echo "   - Switch to Satellite view"
echo "   - Take screenshot of desired area"
echo "   - Crop and save as PNG to: $HOME/ardu_ws/terrain/satellite_texture.png"
echo ""
echo "Recommended size: 2048x2048 or 4096x4096 pixels"
echo ""
echo "Once you have the image, update the world file texture path:"
echo "  <diffuse>file://$HOME/ardu_ws/terrain/satellite_texture.png</diffuse>"
