# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 16:46:07 2023
A script to search for all available cloud-free (as much as possible) imagery for a specified polygon
Currently includes Landsat 8/9 and Sentinel-2

Downloads scaled, true-colour RGBs (8-bit) in tif format.

@author: snasonov
"""

#####
#Define Parameters
rerun = False #is this a rerun? If re-running make sure to delete any incomplete folders, which will be the most recent one
vectors = r"C:\QL\vectors\test_data.shp"
outfolder = r'C:\QL\output'
id_col = 'Obj_ID' #unique ID Column
t1_col = 'T1' #start date column 
t2_col = 'T2' #end date column

#####

import ee
import geemap
import geopandas
import os,math,time
from datetime import datetime as dt
import pandas as pd
import numpy as np
from osgeo import gdal


def main(p):
    # Get image date and reformat 
    def getDate(im):
        return(ee.Image(im).date().format("YYYY-MM-dd"))
    
    #Mosaic by date
    def mosaicByDate(indate):
        d = ee.Date(indate)
        im = col.filterBounds(poly).filterDate(d, d.advance(1, "day")).mosaic()
        return(im.set("system:time_start", d.millis(), "system:index", d.format("YYYY-MM-dd"), "system:date",d.format("YYYY-MM-dd")))
    
    #Apply mosaic by date to a collection
    def runDateMosaic(col_list):
        #get a list of unique dates within the list
        date_list = col_list.map(getDate).getInfo()
        udates = list(set(date_list))
        udates.sort()
        udates_ee = ee.List(udates)
        
        #mosaic images by unique date
        mosaic_imlist = udates_ee.map(mosaicByDate)
        return(ee.ImageCollection(mosaic_imlist))
    
    #Get cloud mask msk_cldprb band
    #if MSK_CLDPRB > 5, then cloud (set to 0)
    def get_cloud_s2(img1):
        clouds = img1.expression("(MSK_CLDPRB > 5) ? 0 "
                                   ": 1",{'MSK_CLDPRB': img1.select('MSK_CLDPRB')}).rename('cloudmsk')
        return(img1.addBands(clouds))
    
    #get cloud bits from landsat QA_pixel band
    def get_cloud_landsat(img1):
        # Bits 3 and 4 are cloud and cloud shadow, respectively.
        cloudShadowBitMask = (1 << 4)
        cloudBitMask = (1 << 3)
        # Get the pixel QA band.
        qa = img1.select('QA_PIXEL')
        #set both flags to 1
        clouds = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cloudShadowBitMask).eq(0)).rename('cloudmsk')
        return(img1.addBands(clouds))
    
    # Apply sentine-2 surface reflectance scaling factors
    def scale_s2(image):
        scaled = image.select(['red','green','blue']).multiply(0.0001)
        out = image.addBands(scaled, None, True)
        return(out.copyProperties(image,image.propertyNames()))
    
    # Apply landsat-8/9 surface reflectance scaling factors ()
    def scale_landsat(image):
        opticalBands = image.select(['blue','green','red']).multiply(0.0000275).add(-0.2)
        return image.addBands(opticalBands, None, True)
    
    # A function that gets percent coverage by a scene
    def classify_extent(img1):
        classes = img1.expression("(red !=0) ? 1 "
                                   ": 0",{'red': img1.select('red')}).rename('c').clip(poly)
        return(classes)
    
    #Set 0 to 1 and 1 to 0 because we want to add up the cloud pixels
    def classify_cc(img1):
        classes = img1.expression("(cloudmsk == 1) ? 0 "
                           ": 1",{'cloudmsk': img1.select('cloudmsk')}).rename('c').clip(poly)
        return(classes)
    
    #Convert nan to zero
    def nan_to_zero(file_path):
        # Open the raster file in "r+" (read and write) mode
        dataset = gdal.Open(file_path, gdal.GA_Update)
    
        # Loop over all bands
        for band in range(1, dataset.RasterCount + 1):
            # Read the band data as a NumPy array
            raster = dataset.GetRasterBand(band).ReadAsArray()
    
            # Convert NaN values to 0
            raster = np.nan_to_num(raster, 0)
    
            # Write to file
            dataset.GetRasterBand(band).WriteArray(raster)
    
        # Close the dataset
        dataset = None

    #define outputfolder
    out = os.path.join(outfolder,str(p))
    
    if not os.path.exists(os.path.join(outfolder,str(p))):
        os.makedirs(os.path.join(outfolder,str(p)))
    
    if not os.path.exists(os.path.join(outfolder,str(p),'tif')):
        os.makedirs(os.path.join(outfolder,str(p),'tif'))
    
    #get poly
    poly = polys.filterMetadata(id_col,'equals',p)
    #get T1 and T2
    startdate = polys_df[polys_df[id_col]==p].iloc[0][t1_col]
    print(startdate)
    enddate = polys_df[polys_df[id_col]==p].iloc[0][t2_col]
    print(enddate)
    
    # using surface reflectance
    cld = 70 #cloud cover filter, 70%
    
    # mosaic by sensor and date and get clouds from metadata
    col = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate(startdate,enddate).filterBounds(poly).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',cld))
    def add_sensor(im):return(im.set("system:sensor", "S2"))
    def common_names(image):return(image.select(['B2','B3','B4','cloudmsk'],['blue','green','red','cloudmsk']))
    
    s2_list = col.toList(col.size())
    s2_mosaic_col = runDateMosaic(s2_list)
    s2_mosaic_col_cld = s2_mosaic_col.map(get_cloud_s2).map(common_names).map(scale_s2).map(add_sensor)
    #s2_md = s2_mosaic_col_cld.getInfo()
    
    col = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate(startdate,enddate).filterBounds(poly).filter(ee.Filter.lt('CLOUD_COVER',cld))
    def add_sensor(im):return(im.set("system:sensor", "L8"))
    def common_names(image):return(image.select(['SR_B2','SR_B3','SR_B4','cloudmsk'],['blue','green','red','cloudmsk']))
    
    l8_list = col.toList(col.size())
    l8_mosaic_col = runDateMosaic(l8_list)
    l8_mosaic_col_cld = l8_mosaic_col.map(get_cloud_landsat).map(common_names).map(scale_landsat).map(add_sensor)
    #l8_md = l8_mosaic_col_cld.getInfo()
    #l8_md
    
    col = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate(startdate,enddate).filterBounds(poly).filter(ee.Filter.lt('CLOUD_COVER',cld))
    def add_sensor(im):return(im.set("system:sensor", "L9"))
    def common_names(image):return(image.select(['SR_B2','SR_B3','SR_B4','cloudmsk'],['blue','green','red','cloudmsk']))
    
    l9_list = col.toList(col.size())
    l9_mosaic_col = runDateMosaic(l9_list)
    l9_mosaic_col_cld = l9_mosaic_col.map(get_cloud_landsat).map(common_names).map(scale_landsat).map(add_sensor)
    #l9_md = l9_mosaic_col_cld.getInfo()
    
    #merge collections
    col_merged = s2_mosaic_col_cld.merge(l8_mosaic_col_cld).merge(l9_mosaic_col_cld)
    fcol = col_merged.sort('system:date')
    #fcol
    
    #rename system:index using system:date and system:sensor
    def renamebySensor(im):
        d = im.get('system:date')
        s = im.get('system:sensor')
        updated = ee.String(d).cat(ee.String('_')).cat(ee.String(s))
        return(im.set("system:newIndex", updated))
    
    renamed = fcol.map(renamebySensor)
    newNames = renamed.aggregate_array('system:newIndex')
    #renamed #debug
    
    ## calculate percent overlap and percent cloud cover in the poly
    # Classify to get coverage and cloud extent
    def classify_extent(img1):
        classes = img1.expression("(red !=0) ? 1 "
                                   ": 0",{'red': img1.select('red')}).rename('c').clip(poly)
        return(classes)
    
    def classify_cc(img1):
        #change 0 to 1, and 1 to 0
        classes = img1.expression("(cloudmsk == 1) ? 0 "
                           ": 1",{'cloudmsk': img1.select('cloudmsk')}).rename('c').clip(poly)
        return(classes)
    
    renamed_extent = renamed.map(classify_extent).toBands().rename(newNames)
    renamed_cc = renamed.map(classify_cc).toBands().rename(newNames)
    
    #Calculate statistics
    reduced_sum = renamed_extent.reduceRegion(reducer=ee.Reducer.sum(),geometry=poly.geometry(),scale=30,maxPixels=100000000).getInfo()
    reduced_count = renamed_extent.reduceRegion(reducer=ee.Reducer.count(),geometry=poly.geometry(),maxPixels=100000000,scale=30).getInfo()
    
    reduced_sum_cc = renamed_cc.reduceRegion(reducer=ee.Reducer.sum(),geometry=poly.geometry(),maxPixels=100000000,scale=30).getInfo()
    reduced_count_cc = renamed_cc.reduceRegion(reducer=ee.Reducer.count(),geometry=poly.geometry(),maxPixels=100000000,scale=30).getInfo()
    
    #Rearrange and calculate percent coverage and percent cloud cover
    #extent
    df_sum = pd.DataFrame([reduced_sum]).T
    df_sum.columns = ['sum']
    
    df_count = pd.DataFrame([reduced_count]).T
    df_count.columns = ['count']
    
    df_perc = df_sum.join(df_count)
    df_perc['percent_coverage'] = (df_perc['sum']/df_perc['count'])*100
    
    #cloud cover
    df_sum_cc = pd.DataFrame([reduced_sum_cc]).T
    df_sum_cc.columns = ['sum_cc']
    
    df_count_cc = pd.DataFrame([reduced_count_cc]).T
    df_count_cc.columns = ['count_cc']
    
    df_perc_cc = df_sum_cc.join(df_count_cc)
    df_perc_cc['percent_cc'] = (df_perc_cc['sum_cc']/df_perc_cc['count_cc'])*100 
    
    #join extent and cc 
    meta_df_ext = df_perc.join(df_perc_cc)
    
    #write to file as a record of all available imagery
    outpath = os.path.join(out,'availableImagery.csv')
    meta_df_ext.to_csv(outpath)
    
    # select only >90% coverage and less than 10% cloud cover
    toExport = meta_df_ext.loc[(meta_df_ext['percent_coverage'] >= 90) & (meta_df_ext['percent_cc'] < 10)]
    id_list = list(toExport.index.values)
    
    #id_list = [id_list[0]] #for debug
    
    ##Prepare region of interest, static buffer
    #roi = poly.geometry().buffer(200) #static buffer of 200m, V1
    
    ##Redo with variable buffer
    poly_area = poly.geometry().area(maxError=1)
    roi = poly.geometry().buffer(poly_area.sqrt())
    
    #export all images to review
    for i in id_list:
        img = renamed.filter(ee.Filter.inList('system:newIndex',ee.List([i]))).first()
        #cloud = img.select("cloudmsk").clip(poly)
        image = img.select(["red","green","blue"])
    
        #export cloud mask if necessary
        #filename = os.path.join(out,'tif','cldmsk_{idx}.tif'.format(idx=i))
        #geemap.ee_export_image(cloud.unmask(9), filename=filename, scale=20, region=roi, file_per_band=True,crs='EPSG:3005')
        
        #Export as 8-bit RGB
        filename2 = os.path.join(out,'tif','rgb_{idx}.tif'.format(idx=i)) 
        viz = {'bands': ['red', 'green', 'blue'], 'min': 0, 'max':0.4, 'gamma': [1.5, 1.5, 1.5]}
        geemap.ee_export_image(image.visualize(**viz),filename=filename2, scale=10, region=roi, file_per_band=False,crs='EPSG:3005')
        
        #last step, set nodata to -9, otherwise 0 becomes NoData in the output tif. 
        dataset = gdal.Open(filename2, gdal.GA_Update)
        for band in range(1, dataset.RasterCount + 1):
            band = dataset.GetRasterBand(band).SetNoDataValue(-9)
            band = None
        dataset = None
    

#### Run process
print('Starting')
#Initialize gee 
ee.Initialize()

#open fires shapefile
polys = geemap.shp_to_ee(vectors)
polys_df = geopandas.read_file(vectors)

if rerun is True:
    poly_list_org = polys_df[id_col].tolist() #some unique identifier
    complete = os.listdir(outfolder)
    poly_list = list(set(poly_list_org)-set(complete))
    print('Rerun. ' + str(len(poly_list)) + ' left.')
else:
    poly_list = polys_df[id_col].tolist() #some unique identifier


# This is to take into account any exceptions and retry
# TODO: add threading for hung downloads

for p in poly_list:
    print('Running ' + str(p))
    retries = 0
    while retries < 3:
        try:
            main(p)
            break
        except:
            retries += 1 
            time.sleep(10) #sleep for 10 seconds
        if retries == 3:
            print(str(p) + ' failed')
            continue
 