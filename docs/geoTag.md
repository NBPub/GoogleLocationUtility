*Information for [geoStrip](/docs/geoTag.md#geoStrip) is below*

#### Function Pages
[Location Processing](/docs/Location%20Processing.md)
• [Location Reporting](/docs/Location%20Reporting.md)
• [Location Filtering](/docs/Location%20Filtering.md)
• [geoStrip](/docs/geoTag.md#geoStrip)
• [Location Mapping](/docs/Mapping.md)

[Getting Started](/docs#getting-started)


# geoTag

[geotag.py](/src/GLU/geotag.py)

**Contents**:
[Invocation](#invocation) • [Requirements](#requirements-inputs) • [Operations](#operations) • 
[Outputs](#outputs) • [CLI Walkthrough](#example) • [Sample Report and Map](#detailed-report-results-map)

## Invocation

`home --geoTag`

`home -pgT`

## Requirements, Inputs

1.  Processed location data in **LocationData** directory
2.  Input: Path of directory with photos to process. 
	- Images must have EXIF date taken tag, `datetime_original`, and dates must be within range of the location data.

#### Configuration.ini  \[geoTag\]
*If a setting specification is empty or cannot be read, the default will be used. After input settings are read, they are presented to user to confirm before continuing with geoTag operation.*

*If the entire geoTag section is missing from Configuration.ini, the operation will be aborted.*

| Parameter | Accepted | Default | Description |
| :----: | --- | --- | --- |
| **subfolders** | Boolean | `True` | If sub-directories are present in specified folder, should their photos also be geoTagged? |
| **overwrite** | Boolean | `False` | Should a location match be written over a photo's existing GPS data? |
| **hemi** | 2-character string | *None* | Hemisphere to assume, in case existing photo tags lack reference. Should contain one of `N`,`S` and/or one of `E`,`W`. |
| **location_data** | Filename of processed data (.parquet) | *prompt selection* | Source data to use for tagging. |
| **timezone** | TZ-Name or `prompt` or `prompt-each`  | `prompt-each` | Prompt-each asks for a timezone for each folder of photos. Specifying a TZ-name or `prompt` will use one TZ for all folders. |
| **flag_time** | Timedelta | `1 day` | Mark location matches greater than specified timedelta. |
| **flag_accuracy** | Integer, >0 | *median of matching dataset* | Mark location matches greater than specified accuracy value. |
| **detailed_report** | Boolean | `True` | Generate detailed report of geoTag operation? |
| **results_map** | Boolean | `True` | Generate maps of photos' location matches? |
| **open_mode** | `Locate`,`Launch`, or `Disable` | `Locate` | Options to interact with outputs at end of operation. |

[more info](/docs#geotag)
	
## Operations

1. Read **Configuration.ini** settings
	- Input prompts as required for unspecified settings
	- Display intended geoTag parameters, y/n prompt to continue

	
2. Prompt for and validate **Photo Folder**
	- Enter folder with photos / sub-directories with photos to geoTag

3. **Gather Candidate Images**

4. **Location Match**, **GPS Tag**
	- find best location record for image
	- attempt to add GPS EXIF tags to cadidate images with matches
	
5. **Save Copies**, **Results Report**
	- Successfully tagged photos are saved in the **Outputs** folder, `Outputs/geotag_<date>`
	- Summary of results, reports, and maps are also saved in the geoTag folder.
	
6. **Exit Options**
	- Possible option to open report folder or open report in default browser.
		- y/n prompt, pressing anything other than "y" is interpreted as "n".

## Outputs

1. ***geotag_\<date\>*** in **Outputs** directory, containing . . .
	- copies of images with newly added GPS data
	- results summary as CSV file
	- *optional* detailed results report as HTML file
	- *optional* interactive map(s) displaying tagged image locations as HTML file(s)

*Example "results-summary.csv"*
![geoTag](/docs/images/geoTag_table.png "Basic results table, organized by folder")

## Example
`home -pgT`
<details>
  <summary>geoTag CLI Walkthrough</summary>
  
  ![geoTag](/docs/images/geoTag_tall.png "CLI walkthrough for geoTag. Note timezone specification is 'prompt-each'")
</details>

## Detailed Report, Results Map

An optional HTML detailed report can be generated with each geoTag operation. It will have information on each image detected, and provide error messages for images that could not be geo-tagged. The images below are snippets of the report generated from the [walkthrough example](/docs/geoTag.md#example) above, though with different timezones. Note that `overwrite` is set to `True`, so images that had existing tags were re-located to the location data match.

<details>
  <summary>Detailed Report</summary>

**Summary table in detailed report**

![report0](/docs/images/geoTag_report_0.png "Basic results table, stylized in detailed report")

**Folder Summary**

![report1](/docs/images/geoTag_report_1.png "Detailed results, file-by-file summary for each folder")

*Images with existing tags have a Map Link to directions*
  - **from:** existing tag 
  - **to:** location match

![report2](/docs/images/geoTag_report_2.png "Detailed results, flagged timedelta and accuracy")

*Images without existing GPS info simply have a link to the matched location*

*Matches outside of the time and/or accuracy settings are marked with a red background*
</details>

<details>
  <summary>Results Map</summary>
	
**Results Map**

![report3](/docs/images/geoTag_report_3.png "Results map showing tagged photos with existing GPS data")

*Markers are placed at the location matches, lines are drawn from the previously tagged location, if applicable.*

![report4](/docs/images/geoTag_report_4.png "Results map, hovering provides additional data")

*Image marker/line visibility can be toggled in the legend. Relevant information is provided when hovering on markers (location matches) or line origins (existing tags).*

</details>

---

# geoStrip

[geostrip.py](/src/GLU/geostrip.py)

**Contents**:
[Invocation](#invocation-1) • [Requirements](#requirements-inputs-1) •
[Operations](#operations-1) • [Outputs](#outputs-1)

## Invocation

`home --geoStrip`

`home -pgS`

## Requirements, Inputs

1.  Input: Path of directory with photos to process. 
	- Images must have EXIF date taken tag, `datetime_original`, and dates must be within range of the location data.

#### Configuration.ini  \[geoStrip\]
*If a setting specification is empty or cannot be read, the default will be used.*

| Parameter | Accepted | Default | Description |
| :----: | --- | --- | --- |
| **subfolders** | Boolean | `True` | If sub-directories are present in specified folder, should their photos also be geoStripped? |
| **open_mode** | `Locate`,`Launch`, or `Disable` | `Locate` | Options to interact with outputs at end of operation. |

[more info](/docs#geostrip)

## Operations

1. Read **Configuration.ini** settings

2. **Validate Photo Folder**, **Gather Candidate Images**

3. **Remove GPS Information**
	
4. **Save Copies**, **Results Report**
	- Successfully stripped photos are saved in the **Outputs** folder, `Outputs/geostrip_<date>`
	- Summary of results are also saved in the geoStrip folder.
	
5. **Exit Options**
	- Possible option to open report folder or open report in default browser.
		- y/n prompt, pressing anything other than "y" is interpreted as "n".

## Outputs

1. ***geostrip_\<date\>*** in **Outputs** directory, containing . . .
	- copies of images with GPS data removed
	- results summary as CSV file

*Example "GeoStrip_results.csv"*

![geoStrip](/docs/images/geoStrip_table.png "Basic results table")
