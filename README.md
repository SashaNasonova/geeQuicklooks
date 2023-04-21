# geeQuicklooks
A set of scripts of to generate quicklooks for a pre-defined vector file that contains start and end date information. Relies on Python Google Earth Engine API and geemap package. 

Installation
---------------------
Install Anaconda (https://docs.anaconda.com/free/anaconda/install/windows/).

In Anaconda Prompt, create a new virtual environment.
```
conda create --name gee_py
```

Then, activate the newly created environment and install geemap and geopandas.
```
conda activate gee_py
conda install -n base mamba -c conda-forge
mamba create -n gee geemap geopandas localtileserver python -c conda-forge
```
To learn more about the amazing geemap package please visit the following github page (https://github.com/gee-community/geemap).

Authenticate GEE
```
python
import ee 
ee.Authenticate()
```
Follow instructions to authenticate gee. Once the account has been authenticated you should be ready to go.

Installing gdal
---------------------
Installing gdal can be challenging. The following works for me but your millage may vary. 

Go to Chrisoph Gohlke's website (https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal) and download the appropriate gdal wheels (e.g. GDAL‑3.4.3‑cp311‑cp311‑win_amd64.whl) to your machine. 

Then go back to Anaconda Prompt and install gdal.
```
pip install <path to wheels> 
```
In my case it was:
```
pip install C:\Users\Downloads\GDAL-3.4.3-cp311-cp311-win_amd64.whl.
```
Check that gdal is functioning
```
python
from osgeo import gdal
```
If this doesn't work for you, there are a number of solutions presented in various forums and articles. 

Warning! Some will suggest to disable your SSL certificate verification to install gdal. You can do this, but I have learned that this is a "play stupid games, win stupid prizes" kind of situation. You may break other packages that require SSL verification and/or upset your IT department. 

Vector file preparation
---------------------
The script expects a shapefile (.shp) with one or more polygons that contains:

- A unique ID field (text)
- A start date (text, yyyy-mm-dd)
- An end date (text, yyyy-mm-dd).

Please see the test data for more information.

Executing Google Earth Engine Script
---------------------
Open up polyQLs.py script and edit lines 14 - 19 to match your data. See example below for the attached test data.
```
rerun = FALSE
vectors = r"C:\QL\vectors\test_data.shp"
outfolder = r'C:\QL\output'
id_col = 'Obj_ID'
t1_col = 'T1'  
t2_col = 'T2'
```
In Anaconda run:
```
python <path to polyQLs.py>
```

Making maps in R
---------------------
This script was written specifically for visualizing the above satellite imagery with various vector data and may be of limited utility for others.




