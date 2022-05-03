# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 2022

@author: NBPub
"""

import click
from pathlib import Path

@click.command()
@click.option('--docs','-d','selection', flag_value='docs', \
              help="Return link to GLU documentation.")
    
@click.option('--docs_read','-dR','selection', flag_value='docs_read', \
              help="Open documentation URL in default browser.")
    
@click.option('--loc_parse','-p','selection', flag_value='loc_parse', \
              help='Parse takeout data, "Records.json", results saved in LocationData directory.')
    
@click.option('--config','-c','selection', flag_value='config', \
              help='Open configuration file, "Configuration.ini", in default editor.')
    
@click.option('--loc_filter','-f','selection', flag_value='loc_filter', \
              help='Filter parsed location data, saved in LocationData directory as "filtered.parquet"')
    
@click.option('--loc_filterOW','-fOW','selection', flag_value='loc_filterOW', \
              help="Filter parsed data and overwrite existing filtered data without prompt.")
    
@click.option('--loc_report','-r','selection', flag_value='loc_report', \
              help="Create Location Report from parsed or filtered data, saved in Outputs directory.")

@click.option('--report_read','-rR','selection', flag_value='report_read', \
          help="Locate or launch generated reports in Outputs directory.")

@click.option('--geoTag','-pgT','selection', flag_value='geoTag', \
      help="Use location data to add GPS data to images in a folder, copies will be saved in Outputs directory.")      
    
@click.option('--geoStrip','-pgS','selection', flag_value='geoStrip', \
      help="Remove GPS data from images in a folder, copies will be saved in Outputs directory.")  
    
@click.option('--loc_map','-m','selection', flag_value='map', \
      help="Generate HTML map from specified time range of location data.")  

def welcome(selection):
    """Welcome to GLU. See available functions below."""
    
    # Option check, if none print file status
    if selection:
        click.secho(f'Selected: {selection}\n', fg='magenta')
    else:
        from .filestatus import filestatus
        filestatus()    
        return            
    
    # Docs, ReadDocs
    if selection == 'docs':
        click.secho('https://github.com/NBPub/GoogleLocationUtility/docs/Getting Started.md', fg='blue')    
    elif selection == 'docs_read':
        click.secho('Opening https://github.com/NBPub/GoogleLocationUtility/docs/Getting Started.md', fg='blue')
        click.launch('https://github.com/NBPub/GoogleLocationUtility/docs/Getting%20Started.md')
    
    # Location Parse
    elif selection == 'loc_parse':
        folder = Path(Path.cwd(),'LocationData')
        if Path(folder,'Records.json').exists() == False:
            click.secho('Records.json file not found in LocationData directory!',fg='red')
            click.secho('Refer to documentation for information on obtaining Takeout data.\n', fg = 'yellow')
            from .filestatus import folder_check
            folder_check()
        else:
            click.secho('Begin location parsing . . .', fg = 'yellow')
            from .location_parse import location_parse
            location_parse(folder, 'Records.json')
    
    # Configuration Editor
    elif selection == 'config':
        file = Path(Path.cwd(),'Configuration.ini')
        click.secho(click.format_filename(file), fg='blue')
        if file.exists():
            click.launch(click.format_filename(file))
        else:
            click.secho('Configuration file, Configuration.ini, not found!\nSome GLU features may be unavailable, and others will fall to defaults.',fg='red')
    
    # Location Filter, Location Filter OW
    elif selection == 'loc_filter':
        from .location_filter import location_filter
        message, color = location_filter(None, None)
        click.secho(message, fg = color)    
    elif selection == 'loc_filterOW':
        from .location_filter import location_filter
        message, color = location_filter(None, 'OW') # Overwrite without prompt
        click.secho(message, fg = color)
       
    # Location Report    
    elif selection == 'loc_report':
        from .create_location_report import create_location_report
        create_location_report()
    
    # Read Report    
    elif selection == 'report_read':
        from .read_report import read_report
        read_report()               
        
    # Geo Tag
    elif selection == 'geoTag':
        from .geotag import geotag
        message, color = geotag()
        click.secho(message, fg = color)
        
    # Geo Strip
    elif selection == 'geoStrip':
        from .geostrip import geostrip
        message, color = geostrip()
        click.secho(message, fg = color)
    
    # Map Generation
    elif selection == 'map':
        from .mapMe import mapMe
        message, color = mapMe()
        click.secho(message, fg = color)       
   
    # suggest --help if no options selected
    else:
        click.secho('\n\nEnter "home --help" to get started.', fg='magenta')
    return