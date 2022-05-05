#### Function Pages
[Location Reporting](/docs/Location%Reporting.md)
• [Location Filtering](/docs/Location%Filtering.md)
• [geoTag and geoStrip](/docs/geoTag.md)
• [Location Mapping](/docs/Mapping.md)

[Getting Started](/docs/Getting%20Started.md)


# Location Processing

[location_parse.py](/src/GLU/location_parse.py)



## Invocation

`home --loc_parse`

`home -p`

## Requirements

1.  *Records.json* in **LocationData** directory

## Operations

1. *Records.json* --> dictionary --> DataFrame
	- May take some time and will consume RAM

2. **Cleaning**
	- Remove all but GPS coordinates, accuracy, source, deviceTag, timestamp. See [location history data information](/docs/Location%20Processing.md#location-history-data-descriptions).
		- Other information may be kept in future versions, in my case they were mostly empty.
	- Remove records with negative accuracy values.
	- Ensure **source** values are all uppercase, "WIFI" and "wifi" should be the same.

3. **Calculations, Conversions**
	- Convert **source** and **deviceTag** data type to *category*.
	- Convert **timestampMs** to pandas *datetime*.
	- Calculate **timeStep** for all but first entry, pandas *timedelta* between a given record and the preceding record.

4. DataFrame --> parquet 
	- save processed data in **LocationData** directory for future use.
	- optimized data types are persisted.
	- parquet provides significant time savings when loading/saving data versus CSV.

5. **Exit Options**
	- Create report or filter processed data while it is still in memory?
		- y/n prompt to generate report, pressing anything other than "y" is interpreted as "n". Slight lag after input may occur.
		- y/n prompt to filter data, pressing anything other than "y" is interpreted as "n".
		
## Outputs

1. *parsed_\<date\>.parquet* in **LocationData** directory
	
<details>
  <summary>loc_parse example</summary>
  
![Parse1](/docs/images/location_parse.png)

*Parsing operation for ~500MB Records.json file*
</details>
	
## Location History Data Descriptions

The following information is copied from *archive_browser.html*, included with Location History [Takeout](https://takeout.google.com/). **Bolded parameters** are persisted during processing. 

> JSON
> The JSON Location History file describes device location signals and associated metadata collected while you were opted into Location History which you have not subsequently deleted.
> * locations: All location records.
> * **timestampMs(int64): Timestamp (UTC) in milliseconds for the recorded location.**
> * **latitudeE7(int32): The latitude value of the location in E7 format (degrees multiplied by 10**7 and rounded to the nearest integer).**
> * **longitudeE7(int32): The longitude value of the location in E7 format (degrees multiplied by 10**7 and rounded to the nearest integer).**
> * **accuracy(int32): Approximate location accuracy radius in meters.**
> * velocity(int32): Speed in meters per second.
> * heading(int32): Degrees east of true north.
> * altitude(int32): Meters above the WGS84 reference ellipsoid.
> * verticalAccuracy(int32): Vertical accuracy calculated in meters.
> * activity: Information about the activity at the location.
> * timestampMs(int64): Timestamp (UTC) in milliseconds for the recorded activity.
> * type: Description of the activity type.
> * confidence(int32): Confidence associated with the specified activity type.
> * **source(string): The source this location was derived from. Usually GPS, CELL or WIFI.**
> * **deviceTag(int32): An integer identifier (specific to Location History) associated with the device which uploaded the location.**
> * platform(string): The platform describing the device along with miscellaneous build information.
> * platformType(string): The platform type of the device. Either ANDROID, IOS or UNKNOWN.
> * locationMetadata: A repeated list of wifi scans consisting of access points. Each access point consists of the signal strength in dBm (decibels per milliwat) and the mac address of the access point.
