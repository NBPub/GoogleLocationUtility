#### Function Pages
[Location Processing](/docs/Location%20Processing.md)
• [Location Filtering](/docs/Location%20Filtering.md)
• [Location Reporting](/docs/Location%20Reporting.md)
• [geoTag and geoStrip](/docs/geoTag.md)

[Getting Started](/docs#getting-started)


# Location Mapping

[mapMe.py](/src/GLU/mapMe.py)

## Invocation

`home --loc_map`

`home -m`

## Requirements

1.  Processed location data in **LocationData** directory
	
## Operations

1. **Read Configuration.ini settings**
	- Input prompts as required for unspecified settings
	- Style by **time** or **frequency**

2. **Load Data, Generate Map**
#### Time
+ Split specified time range into periods, with period size based on span of time range.
+ Gather best location data point for each period, label time as mid-point of period.
+ Color map markers along time gradient.
+ Vary marker size directly with accuracy, marker opacity inversely with accuracy.
#### Frequency
+ Round all location coordinates within time range to 1/100th decimal degree
+ Count entries per rounded location.
+ Color map markers along frequency gradient.
+ Vary marker size and opacity directly with frequency.
	
3. **Save**
	- Save HTML file in **Maps** directory within **Outputs**
	- `Outputs/Maps/MAP-<style_by>_<date>`
	
4. **Exit Options**
	- Possible option to open map folder or open map directly in default HTML browser.
		- y/n prompt, pressing anything other than "y" is interpreted as "n".

## Outputs

1. *MAP-\<style_by\>_\<date\>* in **Outputs/Maps** directory

### Map Examples
**Time**
![Time Map](/docs/images/time_map.png)


**Frequency**
![Frequency Map](/docs/images/frequency_map.png)
