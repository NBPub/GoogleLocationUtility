#### Function Pages
[Location Processing](/docs/Location%20Processing.md)
• [Location Reporting](/docs/Location%20Reporting.md)
• [geoTag and geoStrip](/docs/geoTag.md)
• [Location Mapping](/docs/Mapping.md)

[Getting Started](/docs#getting-started)


# Location Filtering

[location_filter.py](/src/GLU/location_filter.py)

**Contents**:
[Invocation](#invocation) • [Requirements](#requirements) • [Operations](#operations) • 
[Outputs](#outputs) • [CLI Example](#example) • [Overwrite Invocation](#overwrite-without-prompt)

## Invocation

`home --loc_filter`

`home -f`

## Requirements

1.  Processed location data in **LocationData** directory. Filtering is intended for "bulk" location data.

#### Configuration.ini  \[LocationFilter\]
*If a setting specification cannot be read, the filtering operation will be aborted.*

| Parameter | Accepted | Default | Description |
| :----: | --- | --- | --- |
| **accuracy_cutoff** | Integer, > 0 | *aborts without specification* | Location records with accuracy above cutoff value will be removed from the filtered data. |
| **remove_sources** | Comma separated sources  | *None* | Sources to remove. Must match source names displayed in [report](/docs/Location%20Reporting.md#sample-report). |
| **remove_devices** | Comma separated deviceTags | *None* | Devices to remove.  Must match deviceTags displayed in [report](/docs/Location%20Reporting.md#sample-report). |

[more info](/docs#locationfilter)

## Operations

1. Read **Configuration.ini** settings
	- Display intended filtration parameters, y/n prompt to continue
	
2. Check for existing filtered data, prompt for overwrite.
	- Prompt can be [skipped](#overwrite-without-prompt).

3. **Load Data, Apply Filters**
	- Basic before/after stats displayed
	- This information is also saved in *filter_notes.csv* in **LocationData** directory.

4. **Save**
	- save filtered data in **LocationData** directory for future use
	- `filtered.parquet`
	
5. **Exit Options**
	- Create report from filtered  data while it is still in memory?
		- y/n prompt to generate report, pressing anything other than "y" is interpreted as "n". Slight lag after input may occur.

## Outputs

1. *filtered.parquet* in **LocationData** directory

## Example
`home -f`
<details>
  <summary>loc_filter CLI example</summary>
  
![Filter](/docs/images/location_filter.png "Location filtering with one removed device and one removed source.")

</details>

## Overwrite without prompt

`home --loc_filterOW`

`home -fOW`
