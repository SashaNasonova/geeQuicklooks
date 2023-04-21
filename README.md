# geeQuicklooks
A set of scripts of to generate quicklooks for a pre-defined vector file that contains start and end date information. Relies on Python Google Earth Engine API and geemap package. 

Installation
---------------------
Install Anaconda (https://docs.anaconda.com/free/anaconda/install/windows/).

In Anaconda Prompt, create a new virtual environment.
```
conda create --name gee_py
```

Then, activate the newly created environment and install pip.
```
conda activate gee_py
conda install pip
```

Install geemap and geopandas using pip:
```
pip install geemap
pip install geopandas
```
To learn more about the amazing geemap package please visit the following github page (https://github.com/gee-community/geemap).

Authenticate GEE
```
python
import ee 
ee.Authenticate()
```
Follow instructions to authenticate gee. Once the account has been authenticated you should be ready to use gee.

Installing gdal
---------------------
Installing gdal can be challenging. The following works for me but your millage may vary. 
Ensure that you have the latest version of the Microsoft Visual C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/, download and install Visual Studio Build Tools. This will take a while. 

Then go back to Anaconda Prompt and install gdal.
```
pip install gdal
```

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


Making maps in R
---------------------

