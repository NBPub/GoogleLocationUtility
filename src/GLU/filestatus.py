# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 2022

@author: NBPub
"""

import click
from pathlib import Path

# Folder Check, LocationData and Outputs. Can this be moved to some kind of initialization step?
def folder_check():
    if Path(Path.cwd(),'Outputs').exists() == False:
        click.secho('Created folder for various GLU outputs:', fg='yellow')
        click.secho(Path(Path.cwd(),'Outputs'), fg='blue')
        Path(Path.cwd(),'Outputs').mkdir() 
    if Path(Path.cwd(),'LocationData').exists() == False:
        click.secho('Created folder for Location Data, raw and processed:', fg='yellow')
        click.secho(Path(Path.cwd(),'LocationData'), fg='blue')
        Path(Path.cwd(),'LocationData').mkdir()

# "Home" Printout
def filestatus():
    # Package, Version
    from importlib.metadata import version 
    click.secho(f'GLU version {version("GLU")}\n', fg = 'yellow')
    
    folder_check()
    
    # Configuration.ini
    if Path(Path.cwd(),'Configuration.ini').exists():
        click.secho('Configuration File ready: "Configuration.ini"', fg='green')
        click.secho('\tEdit settings with "home --config" or "home -c"', fg='cyan')
    else:
        click.secho('Configuration File not detected, please add "Configuration.ini" to project directory.', fg='red')
        click.secho('\tSee documentation link with "home --docs" or "home -d", open link with "home --docsRead" or "home -dR"', fg='cyan')
        
    # Records.json, Settings.json
    if Path(Path.cwd(),'LocationData','Records.json').exists():
        click.secho('\nTakeout Data available for parsing: "Records.json"', fg='green')
        if Path(Path.cwd(),'LocationData','Settings.json').exists():
            click.secho('Takeout Data Settings availble: "Settings.json"', fg='green')
        else:
            click.secho('Takeout Data Settings not detected, "Settings.json", may provide additional information about devices.', fg='yellow')
    else:
        click.secho('\nTakeout Data not detected. Add "Records.json" to "LocationData" directory to parse locations.',fg = 'yellow')
        click.secho('\tSee documentation link with "home --docs" or "home -d", open link with "home --docsRead" or "home -dR"', fg='cyan')
        
    # Parsed and filtered data
    files = []
    for val in Path(Path.cwd(),'LocationData').iterdir():
        if val.suffix == '.parquet':
            files.append(val.name)          
    if len(files) > 0:
        click.secho('\nProcessed location data is ready:', fg='green')
        for file in files:
            click.secho(f'\t{file}', fg='blue')
        click.secho('GeoTag photos using data with "home --geoTag" or "home -pgT"', fg='cyan')
        click.secho('Remove GPS data from photos with "home --geoStrip or "home -pgS"', fg='cyan')
        click.secho('Create a map  using data with "home --loc_map" or "home -m"', fg='cyan')
    else:
        click.secho('\nProcessed location data not detected in "LocationData" directory.', fg='yellow')
        if Path(Path.cwd(),'LocationData','Records.json').exists():
            click.secho('\tParse Takeout data, "Records.json" with "home --loc_parse" or "home -p"', fg='cyan')
    
    # Reports
    files = {'Location':0, 'GeoTag':0,'GeoStrip':0}
    for val in Path(Path.cwd(),'Outputs').iterdir():
        if val.is_dir() and val.name.startswith('LocationReport_'):
            files['Location'] += 1
        if val.is_dir() and val.name.startswith('geotag_'):
            files['GeoTag'] += 1
        if val.is_dir() and val.name.startswith('geostrip_'):
            files['GeoStrip'] += 1
            
    if sum(files.values()) > 0:
        click.secho('\nReport(s) found in "Outputs" directory:', fg='green')
        for key in files.keys():
            if files[key] > 0:
                click.secho(f'\t{key}: {files[key]}', fg = 'blue')
        click.secho('Read report or open its directory in default browser with "home --report_read" or "home -rR"', fg='cyan')
    else:
        click.secho('\nReports not detected in "Outputs" directory.', fg='yellow')
        
    click.secho('\n\nEnter "home --help" to get started.', fg='magenta')

if __name__ == "__main__":
    pass