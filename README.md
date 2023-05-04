# geeQuicklooks
Generates quicklooks for a pre-defined vector file that contains start and end date information. Relies on Python Google Earth Engine API and geemap package. Requires a Google Earth Engine account (https://signup.earthengine.google.com/). 

Installation
---------------------
Sign up for a Google Earth Engine account if you don't already have one (https://signup.earthengine.google.com/). 

Install Anaconda (https://docs.anaconda.com/free/anaconda/install/windows/).

In Anaconda Prompt, create a new environment called gee.
```
conda create -n gee
```
Activate it,
```
conda activate gee
```
And then install mamba.
```
conda install mamba -c conda-forge
```
Using mamba install geemap and supporting packages from the conda-forge channel.
```
mamba install geemap geopandas localtileserver python -c conda-forge
```
To learn more about the amazing geemap package please visit the following github page (https://github.com/gee-community/geemap).

Install gcloud CLI
---------------------
Follow the instructions from https://cloud.google.com/sdk/docs/install to install Google Cloud CLI. Use the same email address as for Google Earth Engine.

Install gdal
---------------------
Installing gdal can be challenging. The following works for me but your millage may vary. 

Go to Chrisoph Gohlke's website (https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal) and download the appropriate gdal wheels (e.g. GDAL‑3.4.3‑cp311‑cp311‑win_amd64.whl) to your machine. 

Then go back to Anaconda Prompt, make sure that you are in the gee environment (conda activate gee) and install gdal into the gee environment.
```
pip install <path to wheels> 
```
In my case it was:
```
pip install C:\Users\Downloads\GDAL-3.4.3-cp311-cp311-win_amd64.whl.
```
Open python, check that gdal is functioning and authenticate GEE:
```
python
```
Import gdal:
```
from osgeo import gdal
```
Import GEE:
```
import ee 
```
And authenticate GEE.
```
ee.Authenticate()
```
Follow instructions to authenticate gee, you will be lead to a webpage. Once the account has been authenticated you should be ready to go. The message should read "You are now authenticated with gCloud CLI". To get out of the python commands in Anaconda press Ctrl + Z or exit().

A note on gdal
---------------------
If the above installation doesn't work for you, there are a number of solutions presented in various forums and articles. 

Warning! Some will suggest to disable your SSL certificate verification to install gdal. You can do this, but you may break other packages that require SSL verification and/or upset your IT department. 

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
vectors = r"C:\test\vectors\test_data.shp"
outfolder = r'C:\test\output'
id_col = 'Obj_ID'
t1_col = 'T1'  
t2_col = 'T2'
```
In Anaconda run:
```
conda activate gee
python <path to polyQLs.py>
```

Many thanks to the open source community!
---------------------
Wu, Q., (2020). geemap: A Python package for interactive mapping with Google Earth Engine. The Journal of Open Source Software, 5(51), 2305. https://doi.org/10.21105/joss.02305
