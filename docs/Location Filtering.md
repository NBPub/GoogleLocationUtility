# Location Filtering

[location_filter.py](/GLU/src/GLU/location_filter.py)

## Invocation

`home --loc_filter`

`home -f`

## Requirements

1.  Processed location data in **LocationData** directory. Filtering is intended for "bulk" location data.
	
## Operations

1. Check for existing filtered data, prompt for overwrite.

2. **Read Configuration.ini settings**
	- Display intended filtration parameters, y/n prompt to continue

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

## Overwrite without prompt

`home --loc_filterOW`

`home -fOW`
