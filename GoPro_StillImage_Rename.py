# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 10:17:49 2021

This script can be used to complete a batch renaming process for JPEG still images capture using a GoPro, or anything other camera 
unit where the metadata for the image (i.e. time of creation) is written as an EXIF tag. Most consumer and commercial cameras will 
embed this information into the image file.

@author: SnowBe
"""

import exiftool
from pathlib import Path
import re
import os
import pandas as pd

########################################## EDITS THESE VALUES ########################################################################

#String that stores the project or cruise number, could be of the from PACYYYY-XXX or another designation.

project_name = "PAC2022-036"

#Location and name of Dive log file to import.
    
dive_log = pd.read_csv("D:/Dive_Log/Dive_Log.csv")

#Root directory where GoPro video files are stored

root_dir = Path("D:/May 24")

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

tags = ["FileName", "CreateDate"]
with exiftool.ExifTool(r'C:\Users\SnowBe\exiftool.exe') as et:  #Path to exiftool can either be specified directly, as shown here, or added to PythonPath
    metadata = et.get_tags_batch(tags, recordings)

#Convert the metadate extracted by exfitool to a Pandas dataframe
    
metadata_df = pd.DataFrame(metadata)

#Rename the columns to more user friendly column names

metadata_df = metadata_df.rename(columns = {"SourceFile": "SourcePath", "File:FileName": "FileName", "EXIF:CreateDate": "CreatedDate"})


#By default, exiftool seems to extract date time stamps as YYYY:MM:DD, with colon delimeters rather than slashes. Convert these
#delimeters to slashes, then convert this column type to a datetime dtype.

for row, content in metadata_df["CreatedDate"].items():
    match = re.split(":", content)  #Break the timestamp up based on the presence of a colon
    new_timestamp = str(match[0] + "/" + match[1] + "/" + match[2] + ":" + match[3] + ":" + match[4]) #Concatenate parts into a new string
    metadata_df.at[row, "CreatedDate"] = new_timestamp #Overwrite the created date column with a the newly formated timestamps

#Convert the newly created timestamps to a datetime type.
    
metadata_df["CreatedDate"] = metadata_df["CreatedDate"].astype("datetime64[ns]")

#Save a copy of the CreatedData value as a datetime64 data type, for use later.

metadata_df["StartTime"] = metadata_df["CreatedDate"]



############################################### CONVERT DATA TYPES IN DIVE LOG DATAFRAME ##################################################
    
#Convert the start and end transect times to datetime64 data types
    
dive_log["Launch_UTC"] = dive_log["Launch_UTC"].astype("datetime64[ns]")
dive_log["Recovery_UTC"] = dive_log["Recovery_UTC"].astype("datetime64[ns]")

#Convert the time datetime64 time values to integers, for both the dive_log and metadata entries, to facilitate comparisons

dive_log["Launch_UTC"] = pd.to_numeric(dive_log["Launch_UTC"], errors = "coerce")
dive_log["Recovery_UTC"] = pd.to_numeric(dive_log["Recovery_UTC"], errors = "coerce")
metadata_df["CreatedDate"] = pd.to_numeric(metadata_df["CreatedDate"], errors = "coerce")

#################################### MATCH GOPRO VIDEO CREATION TIMES TO DIVE INTERVALS #################################################


#This nested loops through all the video files in the metadata_df, for each of these video files it then loops through the dive log 
#Launch and Recovery times, to search for the interval between the Launch and Recovery times that contains the start time of that video
#the corresponding video file recording name (e.g. P10079) is then retrieved from the same row in the dive_log data frame and appended
#into a new column "Dive_Name" in the metadata_df. If no value is found, the entry in the "Dive_Name" column, is left blank.


metadata_df["Dive_Name"] = "" #New empty column to fill.

for gp_row, gptimes in metadata_df["CreatedDate"].items():
    for index in range(dive_log["Launch_UTC"].size):
        if(dive_log["Launch_UTC"].at[index] < gptimes < dive_log["Recovery_UTC"].at[index]):
            metadata_df["Dive_Name"].at[gp_row] = dive_log["Transect_Name"].at[index]
            break



##################################### RENAME THE GOPRO VIDEO FILES ##################################################################
 
#New column in metadata_df, to be convert to string data type and used for renaming the files. 
#Reformat time to remove blank space, and colon. Cannot contain colons!

metadata_df["TimeReformat"] = metadata_df["StartTime"]     
metadata_df["TimeReformat"] = metadata_df["TimeReformat"].astype("string")

#Remove dashes and colons, and whitespace, so that the timestamp can be used as part of a file path.
for row, content in metadata_df["TimeReformat"].items():
    content = re.sub(":", "", content)  #Remove colons, collapse empty space.
    content = re.sub(" ", "_", content)  #Remove whitespace, replace with underscore.
    content = re.sub("-", "", content)  #Remove dashes, collapse empty space.
    metadata_df.at[row, "TimeReformat"] = content #Overwrite the created date column with a the newly formated timestamps


#Rename the GoPro .MP4 recordings. The file name generate as the dest_path value will take the form of:
#ProjectName_Dive_Name_YYYYMMDD_HHMMSS.MP4
    
for rows, name in metadata_df["SourcePath"].items():
    source_path = name
    dest_path = str(recording_names[rows].parts[0] + recording_names[rows].parts[1] + "\\" + project_name + "_" + str(metadata_df["Dive_Name"].at[rows]) + "_" + str(metadata_df["TimeReformat"].at[rows]) + ".JPG")
    os.rename(source_path, dest_path)




