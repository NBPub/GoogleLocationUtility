#### Function Pages
[Location Processing](/docs/Location%20Processing.md)
• [Location Filtering](/docs/Location%20Filtering.md)
• [geoTag and geoStrip](/docs/geoTag.md)
• [Location Mapping](/docs/Mapping.md)

[Getting Started](/docs#getting-started)

# Location Reporting

[location_report.py](/src/GLU/location_report.py)

**Contents**:
[Invocation](#invocation) • [Requirements](#requirements) • 
[Operations](#operations) • [Outputs](#outputs) • [Sample](#sample-report)


## Invocation

`home --loc_report`

`home -r`

## Requirements

1.  Processed location data in **LocationData** directory. 
    - Optional, *Settings.json* in **LocationData** directory

#### Configuration.ini  \[LocationReport\]
*If a setting specification is empty or cannot be read, the default will be used.*

| Parameter | Accepted | Default | Description |
| :----: | --- | --- | --- |
| **accuracy_split** | Integer, > 0 | `565` | The proportion of data above/below value is reported, and lines are drawn at the value on graphs. |
| **notable_timegaps** | Integer, 1-50 | `20` | Largest timegaps to add to a table in the report. |
| **figure_dpi** | Integer, 100-300 | `100` | Resolution of generated [graphs](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html), dots per inch. |
| **device_maps** | Boolean | `True` | Generate device maps from location data? |
	
## Operations

1. Determine save folder in **Outputs** directory, prompt for rename or overwrite if needed.

2. **Name Devices, Read Configuration.ini settings**
	- Attempt to add device information to report by matching deviceTag in location data with information in *Settings.json*.

3. **Calculations, Graphing**
	- Basic stats for top of report:
		- Time span, observations per hour
		- Data proportion within / outside accuracy split
		- Accuracy and timeStep distributions
		- Notable Timegaps
	- Graphs to investigate **Source**, **deviceTag**:
		- Accuracy distributions for each Sources
		- Accuracy distributions for each Devices
		- Source distribution for each Devices

4. **Device Maps**
	- Generate [frequency maps](/docs/Mapping.md#frequency) for each device.
	
5. **Report Writing**
	- Combine information gathered above into HTML file.
	- Save within determined save folder in **Outputs** directory.

6. **Exit Options**
	- Possible option to open report folder or open report in default HTML browser.
		- y/n prompt, pressing anything other than "y" is interpreted as "n".

## Outputs

1. ***LocationReport_\<type\>_\<date\>*** in **Outputs** directory, containing . . .
	- Report as HTML file, displaying all graphs and linking to all maps
	- Graphs as PNG files
	- device maps as HTML files within "maps" sub-directory

<details>
  <summary>loc_report example</summary>
  
![Report](/docs/images/location_report.png)

</details>

## Sample Report

<details> 
	<summary><h4>Summary, Tables</h4></summary>
  
**Heading**

![Report1](/docs/images/location_report_ex_1.png)

**Accuracy, Timedelta Statistics**

![Report2](/docs/images/location_report_ex_2.png)
	
**Largest Timegaps**

![Report3](/docs/images/location_report_ex_3.png)
	
</details>

<details> 
	<summary><h4>Graphs</h4></summary>
  
**Accuracy by Source**
![plot1](/docs/images/boxer-Accuracy-Source.png)

**Accuracy by Device**
![plot2](/docs/images/boxer-Accuracy-Device.png)

**Source by Device**
![plot3](/docs/images/counter-Source-Device.png)
	
</details>
