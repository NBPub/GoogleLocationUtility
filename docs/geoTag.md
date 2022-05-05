*Information for [geoStrip](/docs/geoTag.md#geoStrip) is below*

# geoTag

[geotag.py](/src/GLU/geotag.py)

## Invocation

`home --geoTag`

`home -pgT`

## Requirements, Inputs

1.  Processed location data in **LocationData** directory
2.  Input: Path of directory with photos to process. 
	- Images must have EXIF date taken tag, `datetime_original`, and dates must be within range of the location data.
	
## Operations

1. **Validate Input Folder**, **Read Configuration.ini settings**
	- Display intended geoTag parameters, y/n prompt to continue
	- Input prompts as required for unspecified settings

2. **Gather Candidate Images**

3. **Location Match**, **GPS Tag**
	- find best location record for image
	- attempt to add GPS EXIF tags to cadidate images with matches
	
4. **Save Copies**, **Results Report**
	- Successfully tagged photos are saved in the **Outputs** folder, `Outputs/geotag_<date>`
	- Summary of results, reports, and maps are also saved in the geoTag folder.
	
5. **Exit Options**
	- Possible option to open report folder or open report in default browser.
		- y/n prompt, pressing anything other than "y" is interpreted as "n".

## Outputs

1. *geotag_\<date\>* in **Outputs** directory

*Example "results-summary.csv"*
![geoTag](/docs/images/geoTag_table.png)

## Example

<details>
  <summary>geoTag CLI Walkthrough</summary>
  
  ![geoTag](/docs/images/geoTag_tall.png)
</details>

## Detailed Report, Results Map

An optional HTML detailed report can be generated with each geoTag operation. It will have information on each image detected, and provide error messages for images that could not be geo-tagged. The images below are snippets of the report generated from the [walkthrough example](/docs/geoTag.md#example) above, though with different timezones. Note that `overwrite` is set to `True`, so images that had existing tags were re-located to the location data match.

<details>
  <summary>Detailed Report</summary>

**Summary table in detailed report**

![report0](/docs/images/geoTag_report_0.png)

**Folder Summary**

![report1](/docs/images/geoTag_report_1.png)

*Images with existing tags have a Map Link to directions*
  - **from:** existing tag 
  - **to:** location match

![report2](/docs/images/geoTag_report_2.png)

*Images without existing GPS info simply have a link to the matched location*

*Matches outside of the time and/or accuracy settings are marked with a red background*
</details>

<details>
  <summary>Results Map</summary>
	
**Results Map**

![report3](/docs/images/geoTag_report_3.png)

![report4](/docs/images/geoTag_report_4.png)

*Markers are placed at the location matches, lines are drawn from the previously tagged location, if applicable.*
</details>

---


# geoStrip

[geostrip.py](/src/GLU/geostrip.py)

## Invocation

`home --geoStrip`

`home -pgS`

## Inputs

1.  Input: Path of directory with photos to process. 
	- Images must have EXIF date taken tag, `datetime_original`, and dates must be within range of the location data.
	
## Operations

1. **Validate Input Folder**, **Read Configuration.ini settings**

2. **Gather Candidate Images**

3. **Remove GPS Information**
	
4. **Save Copies**, **Results Report**
	- Successfully stripped photos are saved in the **Outputs** folder, `Outputs/geostrip_<date>`
	- Summary of results are also saved in the geoStrip folder.
	
5. **Exit Options**
	- Possible option to open report folder or open report in default browser.
		- y/n prompt, pressing anything other than "y" is interpreted as "n".

## Outputs

1. *geostrip_\<date\>* in **Outputs** directory

*Example "GeoStrip_results.csv"*

![geoStrip](/docs/images/geoStrip_table.png)
