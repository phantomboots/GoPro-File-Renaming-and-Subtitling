# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:17:49 2021

@author: SnowBe
"""

import exiftool
from pathlib import Path
import re
import os
import pandas as pd
import time
import math

########################################## EDITS THESE VALUES ########################################################################

#Root directory where GoPro video files are stored

root_dir = Path("D:/GoPro_Video")

#Directory with the NAV files are stored

nav_dir = Path("C:/Users/SnowBe/Documents/Projects/Anchor Scour Cumulative Effects_2021_22/Data/Final_Processed_Data")

#Project Name

project = "Anchor Scour 2021"

###################################### RUN EXIFTOOL TO EXTRACT GOPRO RECORDINGS EXIF TAGS ############################################

#Empty list to hold GoPro files names, this will be filled using the .iterdir() method on the Path object for the root directory 
#where all the files are stored.

recording_names = []


#Iterate through the contents of the root directory, and append the filenames within this directory to the empty list.
for each in root_dir.iterdir():
    recording_names.append(each)
    
#List comprenhension to convert the Path objects in the recording_names list to strings, since exiftool cannot work with Path objects    
    
recordings = [str(files) for files in recording_names]
    
#Instantiate PyExifTool, get the file created date, as well as it's duration.
#May need to revisits specific tags if using different GoPros. Need file name, CreateDate and duration (seconds)

tags = ["FileName", "CreateDate", "Duration"]
with exiftool.ExifTool(r'C:\Users\SnowBe\exiftool.exe') as et:  #Path to exiftool can either be specified directly, as shown here, or added to PythonPath
    metadata = et.get_tags_batch(tags, recordings)

#Convert the metadate extracted by exfitool to a Pandas dataframe
    
metadata_df = pd.DataFrame(metadata)

#Rename the columns to more user friendly column names

metadata_df = metadata_df.rename(columns = {"SourceFile": "SourcePath", "File:FileName": "FileName", "QuickTime:CreateDate": "CreatedDate", "QuickTime:Duration": "DurationSeconds"})


#By default, exiftool seems to extract date time stamps as YYYY:MM:DD, with colon delimeters rather than slashes. Convert these
#delimeters to slashes, then convert this column type to a datetime dtype.

for row, content in metadata_df["CreatedDate"].items():
    match = re.split(":", content)  #Break the timestamp up based on the presence of a colon
    new_timestamp = str(match[0] + "/" + match[1] + "/" + match[2] + ":" + match[3] + ":" + match[4]) #Concatenate parts into a new string
    metadata_df.at[row, "CreatedDate"] = new_timestamp #Overwrite the created date column with a the newly formated timestamps

#Convert the newly created timestamps to a datetime type.
    
metadata_df["CreatedDate"] = metadata_df["CreatedDate"].astype("datetime64[ns]")

#Convert the duration column to an integer, drop the milliseconds.

metadata_df["DurationSeconds"] = metadata_df["DurationSeconds"].astype("int")

#Save a copy of the CreatedData value as a datetime64 data type, for use later.

metadata_df["StartTime"] = metadata_df["CreatedDate"]

#Remove the file extension from the GoPro filename. The regular expression in this loop searches for a period followed by any 3
#characters, and will work for any video file extension type. 

for row, content in metadata_df["FileName"].items():
    pattern = re.compile("\.(\w{3})$") #Match the file extension
    extension = pattern.split(content)
    name_only = str(extension[0])
    metadata_df.at[row, "FileName"] = name_only


###############################################CREATE SECOND BY SECOND TIME SERIES FOR ALL VIDEOS ###########################

#Empty data frame to fill with new timeseries, using same column names as above.

timesdf = pd.DataFrame(data = None, columns = ['date_time', 'FileName'])

#For each unique video file, generate a second by second time series index from the "CreatedDate" timestamp, by corresponding
#Length of the "DurationsSeconds" value for that same video file. Generate a time series indexed DataFrame and append it to the 
#empty dataframe.

for i in range(len(metadata_df)):
    videoseconds = pd.Series(pd.date_range(metadata_df.at[i, "CreatedDate"], periods = metadata_df.at[i, "DurationSeconds"], freq = "S"))
    videotimes = pd.DataFrame({"date_time": videoseconds, "FileName": metadata_df.at[i, "FileName"]}) #Make sure the date_time column has the same column title as the processed NAV data
    timesdf = timesdf.append(videotimes)

################################################READ IN THE PROCESSED NAV DATA ##############################################
    
#Empty list to hold list of files in NAV dir
    
nav_paths = []

#Get file names, append to empty list.

for each in nav_dir.iterdir():
    nav_paths.append(each)

#Read and concatenate the files to a single dataframe in the step below.

navdf = pd.concat((pd.read_csv(f) for f in nav_paths), ignore_index = True)


#Convert the date_time column to a datetime64[ns] dtype

navdf["date_time"] = navdf["date_time"].astype("datetime64[ns]")

###############################################JOIN THE DATA FROM THE NAV FILES TO THE VIDEO TIME SERIES ###################

#Let the time series df be the left data frame; use pd.merge() with a left join, on the 'date_time' column as a key.

mergeddf = pd.merge(timesdf, navdf, how="left", on = "date_time")

###############################################GENERATE AND WRITE A .SRT FILE ##############################################

#Function to generate the .SRT data structure. GoPro recordings are started and stopped while the vehicle is still on deck, and 
#there will be periods when the video is not recording the vehicle on transect. These entries will have 'NaN' values in the 
#mergeddf data frame, and are subtitled as 'OFF TRANSECT' and dealt with seperately by the function below. 

#Input values are a row number (i) and filtered data frame of the mergeddf.

"""
.SRT file data structure examplei shown below. The one line space between entries is required for proper functionality.
    
1
00:00:00 --> 00:00:01    
Text 1 to display
Text 2 to display

2
00:00:01 --> 00:00:02
Text 1 to display
Text 2 to display   
    
"""

def srt_writer(i, df):
    if(math.isnan(df["Beacon_Lat_loess"].at[i])):
        return(
            f'{i+1}\n'
            f'{time.strftime("%H:%M:%S", time.gmtime(i))} --> {time.strftime("%H:%M:%S", time.gmtime(i+1))}\n'
            f'OFF TRANSECT - NO NAV DATA\n'
            f'Dive Number: {re.split("_", df["FileName"].at[0])[1]}\n'
            f'Project: {project}\n'
            f'UTC Timestamp: {df["date_time"].at[i]}\n'
            f'\n'
            )
    else:
        return(
            f'{i+1}\n'
            f'{time.strftime("%H:%M:%S", time.gmtime(i))} --> {time.strftime("%H:%M:%S", time.gmtime(i+1))}\n'
            f'Dive Number: {re.split("_", df["FileName"].at[0])[1]}\n'
            f'Project: {project}\n'
            f'UTC Timestamp: {df["date_time"].at[i]}\n'
            f'Depth_m: {round(df["Depth_m"].at[i], 1)}\n'
            f'ROV Lat: {round(df["Beacon_Lat_loess"].at[i], 5)}\n'
            f'ROV Long: {round(df["Beacon_Long_loess"].at[i], 5)}\n'
            f'Altitude_m: {round(df["Altitude_m"].at[i], 1)}\n'
            f'\n'
            )
    
#Write one .SRT file per video file. Write to the same directory specified as the root directory earlier in this script.

for each in pd.unique(mergeddf["FileName"]): #First level is unique file names
   filtered = mergeddf.loc[mergeddf["FileName"] == each] #Rows in the dataframe corresponding to each unique file name.
   filtered = filtered.reset_index() #Make sure the index is reset to start at 0, for the next nested loop.
   with open( f'{root_dir.joinpath(each)}.srt', 'w') as srt:
       for i in range(len(filtered)): #Row numbers of the subsetted rows
           entry = srt_writer(i, filtered)
           srt.write(entry)
           srt.write('\n')
