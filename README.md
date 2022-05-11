# Google Location Utility
Utility for **Location History** data from Google Takeout.

## Overview
GoogleLocationUtility, ***GLU*** is a command-line interface (CLI) tool for processing and [utilizing](/README.md#Features) location history data from [Google Takeout](https://takeout.google.com/) built with Python. See below for [requirements](/README.md#Requirements) and [installation](/README.md#installation-quickstart) instructions. 
A detailed usage guide is provided in the [documentation](/docs#getting-started).

<img src="https://bestanimations.com/media/earth/998284110earth-spinning-rotating-animation-40.gif" height = 100px alt="bestanimations.com">

### Requirements
**[Python](https://www.python.org/) version 3.8 or newer** is required. See the [beginner's guide](https://wiki.python.org/moin/BeginnersGuide/Download) for help installing Python on your system.

Installing **GLU** within a virtual environment (**venv**) will install all required packages. 
The requirements and versions specified during installation are listed below. A list of all installed packages (output to `pip freeze > requirements.txt`) is provided in the docs, [installed packages](/docs#installed-packages).

* **[Click](https://click.palletsprojects.com/) >= 8.0**, used to build CLI
* **[exif](https://exif.readthedocs.io/) >= 1.3**, reads/adds GPS tags from/to image files
* **[plotly](https://plotly.com/python/) >= 5.6**, generates HTML interactive maps
* **[pandas](https://pandas.pydata.org/pandas-docs/stable/index.html) >= 1.4**, main tool for data handling
* **[numpy](https://numpy.org/doc/stable/) >= 1.22**, used with **pandas** for calculations
* **[matplotlib](https://matplotlib.org/stable/index.html) >= 3.5**, graphing engine for location reports
* **[seaborn](https://seaborn.pydata.org/index.html) >= 0.11.2**, used with **matplotlib**
* **[fastparquet](https://fastparquet.readthedocs.io/en/latest/) >= 0.8**, efficient storage for processed location data
* **[Jinja2](https://jinja.palletsprojects.com/) >= 3.0**, required for **pandas** HTML exports, report building

### Installation, Quickstart
The following steps provide installation instructions within a virtual environment. It may be possible to install and use **GLU** in your base environment, but it is not recommended.

#### 1. In a directory of your creation, `<your-directory>`. Within this folder, create and activate a virtual environment in `venv`.
```
# Unix / macOS
	cd <your-directory>
	python3 -m venv venv
	. venv/bin/activate	
# Windows
	cd <your-directory>
	py -3 -m venv venv
	venv\Scripts\activate
```

The following steps assume you are in `<your-directory>` and the virtual environment is activated. These are accomplished in the first, `cd ...`, and third, `...activate`, lines.

---
#### Option 2A - [PyPi](https://pypi.org/project/GoogleLocationUtility/) installation

**2A.** Install package from PyPi. 
```
# Unix / macOS / Windows
	pip install GoogleLocationUtility
```
  * Download [Configuration.ini](https://raw.githubusercontent.com/NBPub/GoogleLocationUtility/main/Configuration.ini) as `<your-directory>/Configuration.ini`, be sure not to change the file extension.

*Obtain Configuration.ini through command line. Use [curl](https://curl.se/) or [wget](https://www.gnu.org/software/wget/). Note capitilization of "o/O" for curl/wget
```
# Unix / macOS / Windows
	curl https://raw.githubusercontent.com/NBPub/GoogleLocationUtility/main/Configuration.ini -o ./Configuration.ini
	# OR
	wget https://raw.githubusercontent.com/NBPub/GoogleLocationUtility/main/Configuration.ini -O ./Configuration.ini
```

| | | | | |
| :----: | --- | --- | --- | --- |

#### Option 2B - Download and install from Github

**2B.** Download and extract [GLU](https://github.com/NBPub/GoogleLocationUtility/archive/refs/heads/main.zip) into your directory `<your-directory>`. Install package.
- Click the green **Code** button at the top of the page for various download options.
- Note that the "docs" folder can be deleted
```
# Unix / macOS / Windows
	pip install --editable .
```
*Optional, delete docs folder*
```
# Unix / macOS / Windows
	rm -r docs
	rm README.md	
# Windows
	rmdir /s docs
	del README.md
```
---

#### 3. Add Location History [Takeout](https://takeout.google.com/) export.
- Copy location data, *Records.json*, and optionally *Settings.json*, into `<your-directory>/LocationData`.
- Other exported files are not used by **GLU**.
- Enter `home` or `home --help` to get started with **GLU**!

		
#### 4. See [Getting Started](/docs#usage) for detailed usage instructions.
- Modify `<your-directory>/Configuration.ini` to specify various configuration settings.
    - Open configuration file for editing with `home --config`
- Documentation can be accessed from **GLU** with `home --docs` or `home --docs_read`.
- Filestatus and available functions are listed with `home`, all available options are listed with `home --help`.


## Features
For more information about the functions available, see their respective files in [documentation](/docs#getting-started). Configuration settings for the functions are detailed in [Configuration.ini Usage](/docs/Getting%20Started.md#configurationini).
GLU functions stem from the command, `home`, which provides an overview of files and functions available. `home --help` will provide all the function [options](/docs#usage).

![Home1](/docs/images/home_ex1.png "'home' with Configuration.ini, but no Location History data")

*"home" printout before location history added to project folder.*

#### Location History Export
GLU works with exported Location History ***Records*** from Google Takeout. 
***Settings*** are optional, and may provide additional information about devices, which are reported as 10-digit integers in ***Records***. 

***Semantic Location History*** and ***Tombstones*** are not used by GLU. 

After extraction, the exported Location History files from Google should be in **JSON** format.

![Home2](/docs/images/home_ex2.png "'home' with exported, processed, and filtered location data. Configuration.ini and reports also available.)

*"home" printout with location history available, as well as processed data and reports.*

---

### Processing
  - `home --loc_parse` [details](/docs/Location%20Processing.md#location-processing)

Before location data can be used, **Records.json** must be processed. GLU detects **Records.json** within the LocationData folder in the project root: `<your-directory>/LocationData`.

Python's [JSON decoder](https://docs.python.org/3/library/json.html) is used to convert the data into a dictionary (***this process may be memory intensive***), which is then read into a pandas DataFrame.
Timestamps, GPS coordinates, device IDs, and sources are kept from the exported data. Additionally, the timedelta in between each point is calculated. 

The resulting DataFrame is saved as a [Parquet](https://parquet.apache.org/) file, which allows for data type persistence and fast loading/saving, in the **LocationData** directory:
`<your-directory>/LocationData/parsed_<date>.parquet`

![Parse1](/docs/images/location_parse.png "Example of location processing, 'loc_parse'")

*Example processing operation, with ~500MB Records.json file*

### Reports
  - `home --location_report` [details](/docs/Location%20Reporting.md#location-reporting)

Reports can be generated from any processed data. Accuracy and time-delta statistics are presented, along with a breakdown of accuracy against source(s) and device(s).
Maps detailing locations of each device can optionally be generated. Reports are saved as HTML files, static graphs as PNG images, and maps as HTML files.

Each report, containing these files, is saved as a folder in the Outputs directory: `<your-directory>/Outputs/<Report Folder>`.

### Filtering
  - `home --loc_filter` [details](/docs/Location%20Filtering.md#location-filtering)

Processed location data from **Records.json** is considered "bulk" data. These can be further "filtered" by accuracy, source, and device. 
A report for bulk data may be useful in determining filter parameters. Reports can be generated from filtered location data, too.
Notes of filter operations are stored in a CSV table: `<your-directory>/LocationData/filter_notes.csv`.

Results of filter operations are saved as a new Parquet file in the **LocationData** directory:
`<your-directory>/LocationData/filtered.parquet`

### Maps
  - `home --loc_map` [details](/docs/Mapping.md#location-mapping)

Location data within an input time range can be used to generate an interactive HTML map with panning and zooming capabilities. Map markers can be styled by "time" or "accuracy". 
Street tiles from [OpenStreetMap](https://www.openstreetmap.org/) are used in the Plotly graphs, so zooming in provides more detail.

Maps are saved in Outputs/Maps: `<your-directory>/Outputs/Maps/MAP-<style>_<date>.html`

### geoTag
  - `home --geoTag` [details](/docs/geoTag.md#geotag)

You made it! This was my main purpose in building this program. See a [previous version](https://github.com/NBPub/PhotosGeoTagger), and [inspiration](https://github.com/chuckleplant/blog/blob/master/scripts/location-geotag.py).

geoTag can add or replace GPS coordinates to an image's EXIF metadata, provided a suitable match is found in the processed location data. A detailed HTML report of an operation can be saved, including maps of tagged photos.
If a match is made, image copies are saved in the **Outputs** directory: `<your-directory>/Outputs/<geoTag results>`

GPS metadata can also be removed from images in a folder with `home --geoStrip` [details](/docs/geoTag.md#geoStrip). Copies are also saved in the **Outputs** directory. 


## Limitations, Issues
**Altitude** 

Altidude is dropped from the exported Location History in this version, as my data was mostly empty. Altidude (m above sea level) is an available tag for an image's EXIF metadata, provided it's > 0.

**PhotoTag - Improper EXIF tags**

Various failure mechanisms may prevent GPS metadata from being added to an image. These may be endemic to the file itself, but could also be a limitation of my methodology or the package used to read/write EXIF tags. 
In my previous iteration of a photo-tagger, I remember issues with certain panoramas from a mobile phone, images converted from a **[raw image file](https://en.wikipedia.org/wiki/Raw_image_format)**, and older images I didn't know much about.

Verbose errors are captured in a GeoTag detailed report. 

Please [report](https://github.com/NBPub/GoogleLocationUtility/issues) any errors you may encounter.

## Future
Ideas for improvement and future releases:
  * ~~Allow graceful abort with `exit` input for Map settings.~~
  * For settings loads from Configuration.ini, capture Key error for missing specifications. Use default delimiters?
    * ~~Provide link to Configuration.ini base as error/exit message.~~ *added docs link and example code for downloading Configuration.ini*
	* ~~fallback values added to settings load. filecheck with exit also added.~~
  * Implement tests
  * ~~Publish on PyPi~~
  * Utilize Jinja2 HTML templates to clean up code for reports (location report, geotag report)
  * Manual geoTag function, when location match is insufficient. Input coordinates or select on map to tag photo(s)
  * Advanced location report features 
	* Monthly [accuracy](/docs/images/ecdf_ex1.png?raw=1) [ECDFs](/docs/images/ecdf_ex2.png?raw=1)
	* Various analyses presented on [calplot](https://calplot.readthedocs.io/en/latest/), calendar heatmaps
---
	
  * Option for [TimeZoneDB](https://timezonedb.com/) integration to check location vs. input timezone
  * Include additional location history parameters (altitude, velocity, heading, etc . . .)
  * Determine if [Pillow](https://pillow.readthedocs.io/) vs [exif](https://gitlab.com/TNThieding/exif) for tag writing is beneficial.
