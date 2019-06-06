#-------------------------------------------------------------------------------
# Name:        gatherLux_DAY.py
# Purpose:     use arcpy module to take csv generated from daytime data in 
#               illumicloud web app to convert to shapefile in preparation 
#               for inverse distance weighted interpolation in ArcMap
#
# Author:      Theodore Lessman
#
# Created:     11/06/2018
# Copyright:   (c) Theodore Lessman 2018
#-------------------------------------------------------------------------------


# ############################################################
#
#
#___ DAY DATA ___############################################

#___ import statements ___
# handle csv reading
import csv
# arcgis integration
import arcpy
# data access for cursors
from arcpy import da
# environment for workspaces
from arcpy import env
# 3d analyst for IDW
from arcpy.sa import *
# datetime for timestamps
from datetime import datetime

#___ environment settings ___
# ws path
ws = 'R:\\Geog491_5\\Student_Data\\tlessman\\Labs\\IllumiCloud'
# set ws to path
env.workspace = ws
# allow overwrite of files
env.overwriteOutput = 1

# set raster extent
arcpy.env.extent = "-123.08 44.05 -123.06 44.04"

# location of gps path csv
source_day = ws + '\\DayPaths'
# location to put pointcloud shp and gdb
target_day = ws + '\\DayPoints'
# Location to put analysis results
result_day = ws + '\\DayResults'
# shp filename
dayshp = "luxPoints_LIVE_D.shp"

#___ initialize variables needed within pointCloud generation functions ___
# list to hold and arrange points
pointCloud = []
# counter for point indexing
point_cnt = 0

# ###
# ###___ function definitions ___ ###
# ###
#
def iPointLive(f, t, y, x, l):
    # place passed parameters into fields
    FID, timestamp, lat_y, lon_x, lux = f, t, y, x, l
    # create a list of fields
    iPL = [FID, timestamp, lat_y, lon_x, lux]
    #return list
    return iPL

def extractPointsLive(live_file, pc_row):
    # place passed infile parameter in csvfile variable
    csv_file = live_file
    # open in read only
    with open(csv_file, 'rb') as f:
        #read csv
        reader = csv.reader(f)
        #for point (row) in csv
        for point in reader:
            # if 1st row
            if pc_row > 0:
                #read values to create iPoint and add to pointCloud list
                #                            id     t        y        x        l
                pointCloud.append(iPointLive(pc_row,point[1],point[2],point[3],point[4]))
                # print added point
                print pointCloud[pc_row-1]
            #increment row
            pc_row += 1
        # save point row value //not working for tallying point IDs
        point_cnt = pc_row
        #close file
        f.close()

# print count of points in pointCloud
print len(pointCloud)

###
### #for efficiency, work to skip intermediate list pointCloud
###

# use source path as ws
env.workspace = source_day

#___ auto file read ___
# list files in workspace
filelist = arcpy.ListFiles()
# for each file
for file in filelist:
    # get its description
    file_desc = arcpy.Describe(file)
    # get its name
    file_name = file_desc.basename
    # store the full path name
    file_path = source_day + '\\' + file_name + ".csv"
    # extract all rows in file as lists and add to pointCloud list
    extractPointsLive(file_path, point_cnt)

#fc name
fc = dayshp

#___ export to shapefile ___
#create point layer at target with fc name
arcpy.CreateFeatureclass_management(target_day+'\\', fc, "Point")
print 'shapefile created'

# use output ws
env.workspace = target_day

#___ check for field and add if not present ___
# get list of fields in shp
field_list = arcpy.ListFields(fc)
# set index
index = 0
# set lists of names of the fields to be added, their type, and precision
add_list = ['date', 'time', 'lux']
type_list = ['DATE', 'TEXT', 'DOUBLE']
precision_list = ['','',10]
# print contents before add
print fc + " contains:"
for field in field_list:
    print field.name
# for each field to be added
for name in add_list:
    # if the field is not in the shp
    if name not in field_list:
        print "adding " + name
        # add field to shp using name, type and precision as params
        arcpy.AddField_management(fc, name, type_list[index], precision_list[index])
        print('field {} added as {} {} on {}').format(name,type_list[index],precision_list[index],index)
        index += 1

#view updated fields
field_list = arcpy.ListFields(fc)
print fc + " now contains:"
for field in field_list:
    print field.name

# use default ws
env.workspace = ws

#create cursors
#insert cursor for FID geometry
in_cursor = arcpy.da.InsertCursor(target_day + '\\' + fc, ["SHAPE@"])
#update cursor for fields
up_cursor = arcpy.da.UpdateCursor(target_day + '\\' + fc, ['date','time','lux'])

#create point
illumiPoint = arcpy.Point()
#for each item in pointCloud list
pt_cnt = 0
for point in pointCloud:
    #if pointCloud[pt_cnt][4] > 0: #exclude 0 measures
    if pointCloud[pt_cnt][4] >= 0: #include 0 measures
        #id = f
        illumiPoint.ID = point[0]
        #shapeX = lon_x
        illumiPoint.X = float(point[3])
        #shapeY = lat_y
        illumiPoint.Y = float(point[2])
        #insert row in shp with
        in_cursor.insertRow([illumiPoint])
    pt_cnt += 1
#feedback of success
print 'shapefile populated'

# counter for multidemensional indexing through pointCloud
row_cnt = 0
# for each row to be updated
for row in up_cursor:
    #parse timestamp for date and time
    timestamp = datetime.strptime(pointCloud[row_cnt][1], "%Y-%m-%dT%H:%M:%S.%fZ")
    #field = field n of point [row_cnt] in pointCloud (or value)
    row[0] = timestamp
    row[1] = timestamp
    row[2] = pointCloud[row_cnt][4]
    print row
    # execute cursor update
    up_cursor.updateRow(row)
    # increment row_cnt for indexing
    row_cnt += 1
# success feedback
print("{} data points collected.").format(row_cnt)
print 'shapefile updated'
# delete cursors
del up_cursor
del in_cursor


### UNRESOLVED ERROR IN SHP NAME OR CELL SIZE
###
## conduct IDW in spatial analyst
#env.workspace = target_day
#in_point_features = dayshp
#z_field = "lux"
#out_raster = "idw.img"
##cell_size = 1E-05
#
## if available checkout ddd
#if arcpy.CheckExtension("Spatial") == "Available":
#    arcpy.CheckOutExtension("Spatial")
#
#    # Idw (in_point_features, z_field, out_raster, {cell_size}, {power}, {search_radius}, {in_barrier_polyline_features})
#    arcpy.sa.Idw(in_point_features, z_field, out_raster)
#    #check in ddd
#    arcpy.CheckInExtension("Spatial")
##else
#else:
#    #give license warning
#    print "Spatial Analyst license is not available."

