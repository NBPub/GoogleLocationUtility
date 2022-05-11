# Getting Started

**Contents**

[Installation](/docs#Installation) • [Usage](/docs#Usage) • [Configuration.ini - GLU settings](/docs#configurationini)

**Function Pages**
+ [Location Processing](/docs/Location%20Processing.md#location-processing)
+ [Location Reporting](/docs/Location%20Reporting.md#location-reporting)
+ [Location Filtering](/docs/Location%20Filtering.md#location-filtering)
+ [geoTag](/docs/geoTag.md#geoTag)
+ [geoStrip](/docs/geoTag.md#geoStrip)
+ [Location Mapping](/docs/Mapping.md#location-mapping)
	

## Installation

See [Overview](/README.md#installation-quickstart) for installation instructions and steps for activating a virtual environment in the project folder.

## Usage

GLU is called in its active environment with `home`. Simply entering `home` will display the status of your project directory, and suggest actions that can be performed.
Various functions are available by adding an `--option` after `home`.

Enter `home --help` to list all available options and their descriptions. Refer to the function pages linked above for more details.

![help](/docs/images/home_help.png "home --help")

### Inputs

Some functions may ask for user inputs. Inputs come in two flavors:

1. **y/n** - takes the next keystroke as answer, anything other than "y" is interpreted as "n"
2. **General Input** - requires user to specify a parameter within an operation, such as a setting or save location
		- Users are prompted to retry, if entered input is invalid
		- Entering `exit` will abort the operation in most cases. Otherwise try *Ctrl+C* or *Cmd+C* to exit.
		- Many inputs can be set ahead of time and avoided by modifying [*Configuration.ini*](/Configuration.ini), see [below](/docs#configurationini) for details.

![abort](/docs/images/abort_ex.png "abort operation with 'exit'")

---


## Configuration.ini

**Contents**
[LocationReport](/docs#LocationReport) • [LocationFilter](/docs#LocationFilter) • 
[geoTag](/docs#geoTag) • [geoStrip](/docs#geoStrip) • [Map](/docs#Map)
<br/><br/>

`<your-directory>/Configuration.ini` contains specifications for various GLU operations, enter `home --config` to open in default editor. 

The sections of the file are listed and detailed below. Examples of input types are specified within `= <type>`, and defaults or working examples **in bold**.
For example `<integer>` indicates that the setting should be a number, with suggested values of **5** or **333**.
See [boolean](https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.getboolean) for more information on acceptable values.

### LocationReport
[function page](/docs/Location%20Reporting.md#location-reporting)

Location reporting will continue without any specification using default values.

* `accuracy_split = <integer>`
  - Accuracy radius (m) value to highlight. Should be > 0, defaults to **565** ~ 1 sq km.
* `notable_timegaps = <integer>`
  - Determines how many of the (largest) timegaps are displayed in a table. **1** to **50** accepted, defaults to **20**.
* `figure_dpi = <integer>`
  - Figure resolution (matplotlib graphs), in dots per inch. **100** to **300** accpted, defaults to **100**.
* `device_maps = <Boolean>`
  - Option to generate [frequency] maps for each device in location data. Maps are saved as separate HTML files and linked in the report.
		
		
### LocationFilter
[function page](/docs/Location%20Filtering.md#location-filtering)

Location filtering may abort with invalid settings.

* `accuracy_cutoff = <integer>`
  - Remove entries with accuracy value above, worse than, \<integer\>m radius. Should be > 0.
  - *Filter operation stops if cutoff not set.*
* `remove_sources = <source1>, <source2>`
  - Specify sources to remove, comma separate multiple sources (spaces are ignored). Possible sources can be found in a report. Default is None.
  - *Filter operation aborts if there is an error reading sources.*
* `remove_devices = <deviceTag1>, <deviceTag2>`
  - Specify devices to remove, comma separate multiple sources (spaces are ignored). Possible deviceTags can be found in a report. Default is None.
  - *Filter operation aborts if there is an error reading sources.*
		
### geoTag
[function page](/docs/geoTag.md#geoTag)

geoTag will continue without any specification using default values and will prompt for necessary inputs.

* `subfolders = <Boolean>`
  - If sub-directories are present in specified folder, should their photos also be geoTagged? Defaults to **True**
* `overwrite = <Boolean>`
  - Should the GPS match be written over a photo's existing GPS data? Defaults to **False**
* `hemi = <N or S><E or W>`
  - Assume N/S and/or E/W hemisphere for photo's existing GPS tags. Default is None. 
  - Entry is ignored if more than 2 characters, **XYZ**. Only **N, S, E, W** recognized for hemispheres.
	- EXIF tags are saved in [DMS](https://en.wikipedia.org/wiki/Geographic_coordinate_system#Length_of_a_degree), and sometimes the reference is missing which specifies if [DD](https://en.wikipedia.org/wiki/Decimal_degrees) should be positive or negative.
  - examples: **NW** or **N** or **E** or **SE** 
* `location_data = <filename>`
  - Specify processed location data to use. If None or not found, will prompt selection of available files in LocationData directory. 
  - example: **filtered**
* `timezone = <timezone>`
  - **prompt** or **prompt-each** or **\<timezone\>**, defaults to **prompt-each**
  - **prompt** will ask for one timezone to use for all folders within an operation
  - **prompt-each** will ask for a timezone for each folder within an operation
  - **\<timezone\>**, if valid, will be used for all folders within an operation
    - examples: **Europe/Berlin** or **America/Los_Angeles**, see [List of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
    - *Using TZ database name is recommended over TZ abbreviation to let pandas handle daylight savings time, **America/Los_Angeles** vs. **PST***
* `flag_time = <time duration>`
  - Marks image on detailed report if GPS match farther away from photo timestamp than specified duration.
  - examples: **6 hours** or **2 weeks**, see [pandas Timedelta](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Timedelta.html)
  - defaults to **1 day**
* `flag_accuracy = <integer>`
  - Marks image on detailed report if GPS match has accuracy above, worse than, specified value.
  - If None, defaults to median accuracy of matching dataset.
* `detailed_report = <Boolean>`
  - Option to generate HTML report detailing each file/folder in the geoTag operation. Defaults to **True**
  - A high level CSV report is always genearted with each operation.
* `results_map = <Boolean>`
  - Option to save tagged photo locations to an interactive HTML map. Defaults to **True**
  - A maximum of 22 data points are included in one map, multiple maps will be generated for larger result sets.
* `open_mode = <action>`
  - Choose action of prompt at the end of a geoTag operation, defaults to **locate**
    - **launch** - ask to open report in appropriate program
    - **locate** - ask to open report directory
    - **disable** - no questions
		
		
### geoStrip
[function page](/docs/geoTag.md#geoStrip)

geoStrip will continue without any specification using default values.

* `subfolders = <Boolean>`
	- If sub-directories are present in specified folder, should their photos also be geoStripped? Defaults to **True**			
* `open_mode = <action>`
	- Choose action of prompt at the end of a geoStrip operation, defaults to **locate**
		- **launch** - ask to open report in appropriate program
		- **locate** - ask to open report directory
		- **disable** - no questions		
		
### Map
[function page](/docs/Mapping.md#location-mapping)

Location mapping will continue without any specification using default values and will prompt for necessary inputs.

* `location_data = <filename>`
	- Specify processed location data to use. If None or not found, will prompt selection of available files in LocationData directory. 
	- example: **filtered**	
* `style_by = <option>`
	- **time** - specified period is split into periods, a location is gathered for each period. Plot marker color varies with time, marker size and opacity vary with accuracy.
	- **frequency**  - locations within specified is rounded to hundreth decimal degree. Markers are styled (size,color,opacity) according to count of data points at a location.
* `begin = <date>`
* `endin = <date>`
	- Bounding dates to select locations for mapping. Example format: **02/29/20** or **Feb 29 2020**
	- *Note Month/Day/Year in abbreviated example above. I am unsure how pandas handles this formatting for different locales. If you use Day/Month/Year formatting, please report any issues that might arise.*
* `timezone = <timezone>`
	- examples: **Europe/Berlin** or **America/Los_Angeles**, see [List of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
	- will prompt for timezone if input cannot be read or is None.
* `open_mode = <action>`
	- Choose action of prompt at the end of a Map operation, defaults to **locate**
		- **launch** - ask to open report in appropriate program
		- **locate** - ask to open report directory
		- **disable** - no questions	

## Installed Packages

*Example from my venv, 05 May 2022, Python version 3.8.12*

```
click==8.1.3
colorama==0.4.4
cramjam==2.5.0
cycler==0.11.0
exif==1.3.5
fastparquet==0.8.1
fonttools==4.33.3
fsspec==2022.3.0
GoogleLocationUtility==0.1.0
Jinja2==3.1.2
kiwisolver==1.4.2
MarkupSafe==2.1.1
matplotlib==3.5.2
numpy==1.22.3
packaging==21.3
pandas==1.4.2
Pillow==9.1.0
plotly==5.7.0
plum-py==0.8.0
pyparsing==3.0.8
python-dateutil==2.8.2
pytz==2022.1
scipy==1.8.0
seaborn==0.11.2
six==1.16.0
tenacity==8.0.1
```