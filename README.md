# RasterClipper
Scripts that clip raster data based on a shapefile.

## Prerequisites
What things you need to run this script and how to install them
 * The Python Shapefile Library (PyShp):
 * to install use: >>***pip install pyshp***
 * Shapely:
 * to install use: >>***pip install shapely***
 * gdalwarp
 * https://sandbox.idre.ucla.edu/sandbox/tutorials/installing-gdal-for-windows

# How to use the script
 * use: >> ***python script.py -i ./input -o ./output shapefile.shp***
  - -h, --help         show this help message and exit
  - -i INPUT_FOLDER    The path of directory that contains the raster files.
  - -o OUTPUT_PATH     The path of directory where to save the geojson files.
  - -n, --no_run       Do not execute command but save the geojson files.
  - -s, --simulate     Do not execute command and dont write anything on disk.
  - shapefile          The shape file with a field "image_no" in it.
  * use: >>***python script.py -i ./input -o ./output -n -s shapefile.shp***