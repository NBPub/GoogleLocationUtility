# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 2022

@author: NBPub
"""

import click
from pathlib import Path

def read_report():
    # Reports
    files = {}
    folders = {}
    locations = {}
    tags = {}
    strips = {}
    
    for val in Path(Path.cwd(),'Outputs').iterdir():
        # Location Reports
        if val.is_dir() and val.name.startswith('LocationReport_'):
            i = f'L{len(locations)+1}'
            locations[i] = val.name.replace('LocationReport_','')
            folders[i] = val
            if Path(val,'report.html').exists():
                files[i] = Path(val,'report.html')
        # GeoTags
        if val.is_dir() and val.name.startswith('geotag_'):
            i = f'T{len(tags)+1}'          
            tags[i] = val.name.replace('geotag_','')
            folders[i] = val
            if Path(val,'results-detailed.html').exists():
                files[i] = Path(val,'results-detailed.html')
            elif Path(val,'results-summary.csv').exists():
                files[i] = Path(val,'results-summary.csv')               
        # GeoStrips
        if val.is_dir() and val.name.startswith('geostrip_'):
            i = f'S{len(strips)+1}'          
            strips[i] = val.name.replace('geostrip_','')
            folders[i] = val 
            if Path(val,'GeoStrip_results.csv').exists():
                files[i] = Path(val,'GeoStrip_results.csv')

    # Selection
    if len(folders) > 0:        
        click.secho('\nReports in "Outputs" directory:', fg='green')
        if len(locations) > 0:
            click.secho('\nLocation Reports:', fg='yellow')    
            for num, name in locations.items():
                click.secho(f'\t{num}  {name}', fg='cyan')         
        if len(tags) > 0:
            click.secho('\nGeoTag Operations:', fg='yellow')    
            for num, name in tags.items():
                click.secho(f'\t{num}  {name}', fg='cyan')    
        if len(strips) > 0:
            click.secho('\nGeoStrip Operations:', fg='yellow')    
            for num, name in strips.items():
                click.secho(f'\t{num}  {name}', fg='cyan')         
                
        choice = ''
        while choice not in folders.keys():
            choice = input('Enter report key to open: ').upper()   
            if choice == 'EXIT':
                click.secho('Aborted! \n', fg='yellow')
                return
            elif choice in folders.keys():                  
                click.secho(f'\nReport Folder selected:{folders[choice]}\n', fg='green')
                if choice in files:
                    click.secho('Launch report instead of opening directory? (y/n)', fg='cyan') # Open file or file location
                    launch = click.getchar()
                    if launch.lower() == 'y':
                        click.launch(click.format_filename(files[choice]))
                    else:
                        click.launch(click.format_filename(files[choice]), locate = True)                
                else:
                    click.launch(click.format_filename(folders[choice]))                    
                return
            else:
                click.secho(choice.upper(), fg='red')
                click.secho("Invalid entry, ensure it's on the list and a LetterNumber (x2). \n", fg='magenta')
    else:
        click.secho('No reports found in "Outputs" directory', fg='yellow')
        return
    
if __name__ == "__main__":
    pass