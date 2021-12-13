# GoPro-File-Renaming-and-Subtitling
Python scripts to batch rename GoPro files using dive log information, and to generate .SRT subtitles

**GoPro Rename.py**

Script to batch rename GoPro files using the timestamps entered in a DiveLog.csv file. This script is built to work on Windows, not tested on other platforms. The script assumes that GoPro files are recorded as .MP4, and that a dive log has been made (and QA/QC completed). The dive log should have, at a minimum, three columns: Dive Number (e.g. P1XXXX), Launch time in UTC, and Recovery on deck time in UTC. Timestamps must include both date and time, in an unambiguous format (i.e. YYYY-MM-DD HH:MM:SS).

This script also makes use of Python bindings to an executable called exiftool. This executable must be located in a directory on the local machine running this script, and the directory must be accessible. The name of this directory must be entered into the relevant location in the script.
