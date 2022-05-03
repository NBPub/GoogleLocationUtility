# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 2022

@author: NBPub
"""

import pandas as pd
from pathlib import Path
from time import asctime
from .settings_loader import config_load, source_folder
from exif import Image
import click

def geostrip():
    # Choose Folder
    source = source_folder('geoStrip')
    if source == 'exit':
        return 'Aborted!', 'yellow'
    else:
        click.secho(click.format_filename(source),fg='blue')
        click.secho('geoStrip folder set\n\n', fg='green')

    # Settings Read
    subfolders, open_mode = config_load('geoStrip')

    # Get subdirectories, if any
    if subfolders:
        import glob
        folders = [Path(val) for val in glob.glob(f'{str(source)}/**/*/', recursive = True)]
        folders.insert(0,source)
        del glob
    else:
        folders = [source]

    formats = ['.jpg','.jpeg','.png','.tiff', '.bmp', '.heic', '.gif'] # known image formats
    gps_tags = ['gps_latitude_ref', 'gps_longitude_ref', 'gps_latitude', 'gps_longitude', 'gps_altitude']
    available = pd.DataFrame(columns = ['Others','Images', 'withoutGPS','withoutEXIF', 'Candidates', 'Stripped', 'Failed'])
    attempt = {}

    # Search specified source folder, gather photos to strip
    click.secho(f'Scanning images in {len(folders)} folders . . .',fg = 'yellow')
    for folder in folders:            
        others = 0
        images = 0
        candidates = 0
        withoutGPS = 0
        withoutEXIF = 0
        
        for val in folder.iterdir():
            if val.suffix.lower() in formats:
                images += 1
                with open(val, 'rb') as file:
                    image = Image(file)
                    if image.has_exif:                    
                        check = [tag for tag in gps_tags if tag in dir(image)]
                        if check != []:                            
                            attempt[val] = val.name
                            candidates += 1
                        else:
                            withoutGPS += 1
                    else:
                        withoutEXIF += 1
                    del image                    
            elif val.is_dir() == False:
                others += 1            
        
        available.loc[folder,'Others'] = others
        available.loc[folder,'Images'] = images
        available.loc[folder,'withoutGPS'] = withoutGPS
        available.loc[folder,'withoutEXIF'] = withoutEXIF
        available.loc[folder,'Candidates'] = candidates
        available.loc[folder,'Stripped'] = 0
        available.loc[folder,'Failed'] = 0
    
    if len(attempt) == 0:
         return f"No images to strip in {str(source)}", "red"  
    
    # Source folder contents summary
    click.secho(f'Found {available.Images.sum()} images',fg = 'green')
    click.secho(f'\t{available.withoutEXIF.sum()} without EXIF tags',fg = 'magenta')
    click.secho(f'\t{available.withoutGPS.sum()} without GPS data',fg = 'magenta')
    click.secho(f'\t{available.Candidates.sum()} to attempt',fg = 'green')

    # Make folder for copies
    savetime = asctime().replace(":","•")
    savefolder = Path(Path.cwd(),'Outputs',f'geostrip_{savetime}')

    if savefolder.exists():
        click.secho('\n\nResults may overwrite previous attempts, target save folder exists:', fg = 'yellow')
        click.secho(click.format_filename(savefolder),fg='blue')
    else:
        savefolder.mkdir()
        click.secho('\n\nSaving results to folder:', fg = 'yellow')
        click.secho(click.format_filename(savefolder),fg='blue')
   
    # Attempt strip, keep only high level stats in "Available", keep note of errors
    failed = {}    
    for path,filename in attempt.items():
        try:
            image = Image(path)
            for tag in gps_tags:
                if tag in dir(image):
                    image.delete(tag)             
            if path.parent != source:
                if Path(savefolder, path.parent.name).exists() == False:
                    Path.mkdir(Path(savefolder, path.parent.name))
                with open(Path(savefolder, path.parent.name, filename), 'wb') as image_copy:
                    image_copy.write(image.get_file())
            else:
                with open(Path(savefolder, filename), 'wb') as image_copy:
                    image_copy.write(image.get_file())         
            available.loc[path.parent,'Stripped'] += 1       
        except Exception as e:
            available.loc[path.parent,'Failed'] += 1
            failed[filename] = str(e)
    
    # Save + Print results, offer to save failures if any failed.
    available.to_csv(Path(savefolder, 'GeoStrip_results.csv'))
    
    if available.Stripped.sum() > 0:
        click.secho(f'\nGPS data removed from {available.Stripped.sum()} images, copies added to folder',fg = 'green')
    else:
        click.secho('\nNo GPS data removed!',fg = 'yellow')        
    if available.Failed.sum() > 0:
        click.secho(f'\nData removal failed for {available.Failed.sum()} images',fg = 'magenta')
        click.secho('\tSave failure mode(s) with results? (y/n):', fg = 'cyan', nl = False)
        to_save = click.getchar()
        if to_save.lower() == 'y':       
            with open(Path(savefolder,'failures.txt'), mode = 'w') as f:
                for filename, error in failed.items():
                    f.write(f'{str(filename.parent)}, {filename.name}, {error},\n\n')
    
    # Offer to open / locate the results   
    if open_mode == 'locate':
        click.secho('\nOpen results folder? (y/n):', fg = 'cyan', nl = False)
        to_open = click.getchar()
        if to_open.lower() == 'y': 
            click.launch(click.format_filename(Path(savefolder, 'GeoStrip_results.csv')), locate = True)
    
    elif open_mode == 'launch':
        click.secho('\nOpen results file? (y/n):', fg = 'cyan', nl = False)
        to_open = click.getchar()
        if to_open.lower() == 'y': 
            click.launch(click.format_filename(Path(savefolder, 'GeoStrip_results.csv')))

    return "\n\nFinished GeoStrip operation", "green"