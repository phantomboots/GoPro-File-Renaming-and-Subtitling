# GoPro-File-Renaming-and-Subtitling
Python scripts to batch rename GoPro files using dive log information, and to generate .SRT subtitles

**GoPro Rename.py**

Script to batch rename GoPro files using the timestamps entered in a DiveLog.csv file. This script is built to work on Windows, not tested on other platforms. The script assumes that GoPro files are recorded as .MP4, and that a dive log has been made (and QA/QC completed). The dive log should have, at a minimum, three columns: Dive Number (e.g. P1XXXX), Launch time in UTC, and Recovery on deck time in UTC. Timestamps must include both date and time, in an unambiguous format (i.e. YYYY-MM-DD HH:MM:SS).

This script also makes use of Python bindings to an executable called exiftool. This executable must be located in a directory on the local machine running this script, and the directory must be accessible. The name of this directory must be entered into the relevant location in the script.

The script will extract the start time from the GoPro file exif media tags, using the exiftool. This process assumes that the time was set properly on the GoPro!!! If the time was not set ont the GoPro at the time of video recording, this script will not function. 

The script compares the GoPro file start time to the time periods between vehicle Launch off deck and recovery on deck. If a GoPro file recording was started between a given Launch & Recovery interval, the GoPro file is given the name of the dive associated with this time interval. The date-time stamp is also appended from the file name -- this date time stamp is retrieve from the records generated by exiftool, which is assumed to be th most accurate data source. It does not pull any timestamp from the dive log. 

Renamed files are put in the same directory as the input file set -- this behaviour could be easily modified by altering the value of 'dest_path', near the end of this script.

**GoPro Subtitler**

In progress.
