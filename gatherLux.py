#-------------------------------------------------------------------------------
# Name:        gatherLux
# Purpose:  reads in data from a directory containing multiple csv files
#   of GPS log paths, which are transormed into a point cloud with an
#   assigned simulated lux
# Final dataset in shp and gdb has a list of points with fields:
#   [FID, @Shape{lat_y, lon_x, elv_z}, id, date (or timestamp), accuracy, battery, lux]
#
# Author:      tlessman
#
# Created:     15/05/2018
# Copyright:   (c) tlessman 2018
# Licence:     UO GEOG Educational
#-------------------------------------------------------------------------------

# Goals:
### FIXED- ADD FIELD NOT WORKING
### # it was that i put the parameters into a list
    ## in target dir
    ## implemented check for field first
    ## placed addfield into into loop which pulls from lists
    ## removed list around add field parameters
### LATER - add gdb export for proper datetime in single field
###

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
import time

#___ environment settings ___
# ws path
ws = 'R:\\Geog491_5\\Student_Data\\tlessman\\Labs\\IllumiCloud'
# set ws to path
env.workspace = ws
# allow overwrite of files
env.overwriteOutput = 1
# set raster extent
arcpy.env.extent = "-123.08 44.05 -123.06 44.04"

#___ set paths ___
# location of gps path csv
source_dir = ws + '\\Paths'
# location to put pointcloud shp and gdb
target_dir = ws + '\\Points'
# Location to put analysis results
result_dir = ws + '\\Results'
# shp filename
outshp = "luxPoints_SIM.shp"
# gdb filename
#outgdb = "luxPoints.gdb"

#___ initialize variables needed within pointCloud generation functions ___
# list to hold and arrange points
pointCloud = []
# counter for point indexing
point_cnt = 0

# ###
# ###___ function definitions ___ ###
# ###

#___ iPoint definition ___
#
#   creates a list which holds values supplied as parameters, used to create rows for extractPoints()
#
#   data structure of pointCLoud:
# index       0           1        2        3        4        5        6         7
# field       fid         y        x        z        time     accuracy battery   lux
# from csv    (iPoint(row,point[1],point[2],point[3],point[0],point[4],point[16],luxlist[row%len(luxlist)]))
#
def iPoint(f, y, x, z, t, a, b, l):
    # place passed parameters into fields
    FID, lat_y, lon_x, elev_z, timestamp, accuracy, battery, lux__SIM = f, y, x, z, t, a, b, l
    # create a list of fields
    iPt = [FID, lat_y, lon_x, elev_z, timestamp, accuracy, battery, lux__SIM]
    #return list
    return iPt

#
#___ extractPoints definition ___
#
#   gets data from csv files and appends each row as an iPoint(), used to make a list of lists pointCloud
#       * simulated lux values are added for demonstration purposes
#
#   data structure of csv file
# index     #0                        1         2           3         4         5       6     7          8        9    10   11   12          13            14     15       16      17
# field     #time                    ,lat      ,lon        ,elevation,accuracy ,bearing,speed,satellites,provider,hdop,vdop,pdop,geoidheight,ageofdgpsdata,dgpsid,activity,battery,annotation
# example   #2018-03-12T07:00:01.000Z,44.045616,-123.071978,113      ,4.5509996,94.4   ,1.34 ,15        ,gps     ,0.6 ,0.7 ,1   ,-19        ,             ,      ,        ,54     ,
#
def extractPoints(in_file, pc_row):
    # generate simulated lux values to be inserted using modulus
    luxlist = [0, 8, 32, 128, 256, 198, 156, 128, 96, 64, 32, 8, 4, 2, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # place passed infile parameter in csvfile variable
    csv_file = in_file
    # open in read only
    with open(csv_file, 'rb') as f:
        #read csv
        reader = csv.reader(f)
        #for point (row) in csv
        for point in reader:
            # if 1st row
            if pc_row > 0:
                #read values to create iPoint and add to pointCloud list
                #                        id     x        y        z        t        a        b         l
                pointCloud.append(iPoint(pc_row,point[1],point[2],point[3],point[0],point[4],point[16],luxlist[pc_row%len(luxlist)]))
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
env.workspace = source_dir

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
    file_path = source_dir + '\\' + file_name + ".csv"
    # extract all rows in file as lists and add to pointCloud list
    extractPoints(file_path, point_cnt)

###___ manual file read ___
###extractPoints(source_dir + '\\' + "i311" + ".csv", point_cnt)
###extractPoints(source_dir + '\\' + "i312" + ".csv", point_cnt)
###extractPoints(source_dir + '\\' + "i427" + ".csv", point_cnt)
###extractPoints(source_dir + '\\' + "i429" + ".csv", point_cnt)
###extractPoints(source_dir + '\\' + "i638" + ".csv", point_cnt)
###extractPoints(source_dir + '\\' + "i803" + ".csv", point_cnt)

#fc name
fc = outshp

#___ export to shapefile ___
#create point layer at target with fc name
arcpy.CreateFeatureclass_management(target_dir+'\\', fc, "Point")
print 'shapefile created'

# use output ws
env.workspace = target_dir

#___ check for field and add if not present ___
# get list of fields in shp
field_list = arcpy.ListFields(fc)
# set index
index = 0
# set lists of names of the fields to be added, their type, and precision
add_list = ['date', 'time', 'accu', 'batt', 'lux', 'elev']
type_list = ['DATE', 'TEXT', 'DOUBLE', 'SHORT', 'DOUBLE', 'DOUBLE']
precision_list = ['','',10,'',10,20]
# print contents before add
print fc + " contains:"
for field in field_list:
    print field.name
# for each field to be added
for name in add_list:
    # if the field is not in the shp
    if name not in field_list: #not actually skipping existing names
        print "adding " + name
        # add field to shp using name, type and precision as params
        arcpy.AddField_management(fc, name, type_list[index], precision_list[index]) #how to get index for other lists without counter?
        print('field {} added as {} {} on {}').format(name,type_list[index],precision_list[index],index)
        index += 1

#view updated fields
field_list = arcpy.ListFields(fc)
print fc + " now contains:"
for field in field_list:
    print field.name

###__manual add fields__
###arcpy.AddField_management(fc, ['timestamp', 'DATE'])
###print 'timestamp added'
###arcpy.AddField_management(fc, ['accuracy', 'DOUBLE', 10])
###print 'accuracy added'
###arcpy.AddField_management(fc, ['battery', 'SHORT'] )
###print 'battery added'
###arcpy.AddField_management(fc, ['lux', 'DOUBLE', 10])
###print 'lux added'

# use default ws
env.workspace = ws

#create cursors
#insert cursor for FID geometry
in_cursor = arcpy.da.InsertCursor(target_dir + '\\' + fc, ["SHAPE@"])
#update cursor for fields
up_cursor = arcpy.da.UpdateCursor(target_dir + '\\' + fc, ['date','time','accu','batt','lux','elev'])

#create point
illumiPoint = arcpy.Point()
#for each item in pointCloud list
pt_cnt = 0
for point in pointCloud:
    #if pointCloud[pt_cnt][7] > 0: #exclude 0 measures
    if pointCloud[pt_cnt][7] >= 0: #include 0 measures
        #id = f
        illumiPoint.ID = point[0]
        #shapeX = lon_x
        illumiPoint.X = point[2]
        #shapeY = lat_y
        illumiPoint.Y = point[1]
        #shapeZ = elev_z
        illumiPoint.Z = point[3]
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
    dateobj = datetime.strptime(pointCloud[row_cnt][4], "%Y-%m-%dT%H:%M:%S.%fZ")
    timestamp = time.mktime(dateobj.timetuple())
    timestr = datetime.fromtimestamp(timestamp/1000).strftime("%H:%M:%S.%f")
    #field = field n of point [row_cnt] in pointCloud (or value)
    #row[0] = datestamp
    #row[1] = datestamp
    row[0] = dateobj
    row[1] = timestr
    row[2] = pointCloud[row_cnt][5]
    row[3] = pointCloud[row_cnt][6]
    row[4] = pointCloud[row_cnt][7]
    row[5] = pointCloud[row_cnt][3]
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

###
# conduct IDW in spatial analyst
env.workspace = target_dir
in_point_features = outshp
#live debug
#env.workspace = ws + '\\LivePoints'
#in_point_features = "luxPoints_0611_LIVE.shp"
z_field = "lux"
out_raster = "idw_lux.img"
cell_size = 0.75E-05

# if available checkout ddd
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")

    # Idw(in_point_features, z_field, out_raster, {cell_size}, {power}, {search_radius}, {in_barrier_polyline_features})
    arcpy.sa.Idw(in_point_features, z_field, out_raster, cell_size)
    #check in ddd
    arcpy.CheckInExtension("Spatial")
#else
else:
    #give license warning
    print "Spatial Analyst license is not available."

###
### future TODO # add gdb export to preserve full datetime object without spliting data
###

#___ export to gdb ___
#create point layer at target with fc name
#fc = outgdb
#arcpy.CreateFileGDB_management(target_dir+'\\', fc)

# ...

