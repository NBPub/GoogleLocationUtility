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

## Example

<details>
  <summary>geoTag CLI Walkthrough</summary>
  
  ![geoTag](/docs/images/geoTag_tall.png)
</details>

## Detailed Report Features

To be bragged about soon.


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
