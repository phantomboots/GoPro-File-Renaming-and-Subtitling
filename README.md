# GoPro-File-Renaming-and-Subtitling
Python scripts to batch rename GoPro files using dive log information, and to generate .SRT subtitles

**GoPro Rename.py**

Script to batch rename GoPro files using the timestamps entered in a DiveLog.csv file. This script is built to work on Windows, not tested on other platforms. The script assumes that GoPro files are recorded as .MP4, and that a dive log has been made (and QA/QC completed). The dive log should have, at a minimum, three columns: Dive Number (e.g. P1XXXX), Launch time in UTC, and Recovery on deck time in UTC. Timestamps must include both date and time, in an unambiguous format (i.e. YYYY-MM-DD HH:MM:SS).

This script also makes use of Python bindings to an executable called exiftool. This executable must be located in a directory on the local machine running this script, and the directory must be accessible. The name of this directory must be entered into the relevant location in the script.

The script will extract the start time from the GoPro file exif media tags, using the exiftool. This process assumes that the time was set properly on the GoPro!!! If the time was not set ont the GoPro at the time of video recording, this script will not function. 

The script compares the GoPro file start time to the time periods between vehicle Launch off deck and recovery on deck. If a GoPro file recording was started between a given Launch & Recovery interval, the GoPro file is given the name of the dive associated with this time interval. The date-time stamp is also appended from the file name -- this date time stamp is retrieve from the records generated by exiftool, which is assumed to be th most accurate data source. It does not pull any timestamp from the dive log. 

Renamed files are put in the same directory as the input file set -- this behaviour could be easily modified by altering the value of 'dest_path', near the end of this script.

**GoPro Subtitler.py**

This script should be run after running GoPro Rename.py, it does not rename any GoPro files on its own. It is also only tested on windows.

This script also makes use of Python bindings to an executable called exiftool. This executable must be located in a directory on the local machine running this script, and the directory must be accessible. The name of this directory must be entered into the relevant location in the script.

The script will use exiftool to read in the File Names, created data and duration (seconds) for each video file in the directory that the user specifies. Next, a new data frame is built with one record for each second of each video file in the user specified directory. A column of YYYY-MM-DD HH:MM:SS is generated to hold each of these timestamps. File Name is retained as second column.

A processed NAV data file (made using NDST R scripts in the Phantom Data Processing Repository on this github) is read in as a data frame, and should contain a full 1 Hz time series of data collected by the vehicle that the GoPro was mounted on. This includes time, depth, lat/long, altitude, heading, etc. The video time stamp dataframe 
is merged with the video time stamp data frame (left join). The resulting merged data frame will contain NAV data values for the portion of the time that the recorded GoPro files were on transect, but no NAV data for the portions of the video that were off transect. This is due to the fact that the NAV data processing scripts only extract that data that was on transect. 

A function is implemeneted to generate the .SRT data structure (https://docs.fileformat.com/video/srt/#:~:text=SRT%20(SubRip%20file%20format)%20is,content%20after%20it%20is%20produced). For portions of the GoPro recording that are 'off transect' the .SRT shows the dive number, the UTC time and 'OFF TRANSECT' on the subtitle. When on transect, the subtitle will contain the dive number, UTC timestamp, smoothed ROV lat/long, depth and altitude.

**GoPro Still Image Rename**

This script also makes use of Python bindings to an executable called exiftool. This executable must be located in a directory on the local machine running this script, and the directory must be accessible. The name of this directory must be entered into the relevant location in the script.

The script will use exiftool to read in the File Names and created data for each JPEG file in the directory that the user specifies. A column of YYYY-MM-DD HH:MM:SS is generated to hold each of these timestamps. File Name is retained as second column.

The script compares the imaged capture time to the time periods between vehicle Launch off deck and recovery on deck. If a GoPro still image was captured between a given Launch & Recovery interval, the GoPro file is given the name of the dive associated with this time interval. The date-time stamp is also appended from the file name -- this date time stamp is retrieve from the records generated by exiftool, which is assumed to be th most accurate data source. It does not pull any timestamp from the dive log. 

Renamed files are put in the same directory as the input file set -- this behaviour could be easily modified by altering the value of 'dest_path', near the end of this script.
