# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 2022

@author: NBPub
"""

import pandas as pd
import numpy as np
import bisect
from pathlib import Path
from .settings_loader import config_load, source_folder
from .geotag_report import geotag_report
from time import asctime, time
from exif import Image
import warnings
import click

# Coordinate unit conversion DD to DMS, want to name DMX so badly
def DMS(x, coordinate): 
    if coordinate == 'Lat':
        low = 'S'
        high = 'N'
    elif coordinate == 'Lon':
        low = 'W'
        high = 'E'
    if x < 0:
        DMS_ref = low
        x = abs(x)
    else:
        DMS_ref = high       
    Deg = np.floor(x)
    remains = 60*(x - Deg)
    Min = np.floor(remains)
    Sec = round(60*(remains - Min),3)   
    return (Deg, Min, Sec), DMS_ref

def geotag():
    # Choose Folder
    source = source_folder('geoTag')
    if source == 'exit':
        return 'Aborted!', 'yellow'
    else:
        click.secho(click.format_filename(source),fg='blue')
        click.secho('geoTag folder set\n\n',fg='green')

    # Settings Read, confirm continue
    subfolders, overwrite, hemi, location_data_path, timezone, flag_accuracy, flag_time, detailed_report, open_mode, photomap, = config_load('geoTag')
    click.secho('\n\nContinue with GeoTag operation? (y/n):', fg = 'cyan', nl = False)
    to_open = click.getchar()
    if to_open.lower() != 'y': 
        return '\nAborted', 'yellow'
        
    # Get subdirectories, if any
    if subfolders:
        import glob
        folders = [Path(val) for val in glob.glob(f'{str(source)}/**/*/', recursive = True)]
        folders.insert(0,source)
        del glob
    else:
        folders = [source]
    
    # Pre-Allocation
    formats = ['.jpg','.jpeg','.png','.tiff', '.bmp', '.heic', '.gif'] # known image formats
    gps_tags = ['gps_latitude', 'gps_latitude_ref', 'gps_longitude', 'gps_longitude_ref'] # EXIF GPS tags
    available = pd.DataFrame(columns = ['Others','Images','withoutDate', 'withGPS', 'Candidates', 'Tagged', 'Failed', 'OOB']) # Summary DataFrame
    attempt = {} # Images to attempt, path and date taken
    error_report = pd.DataFrame(columns = ['Folder','Filename', 'Error']) # Error Summary DataFrame
    skiptime = pd.DataFrame(columns = ['Folder','Filename']) # Images without date taken
    skiptime_count = 0
    skipGPS = pd.DataFrame(columns = ['Folder','Filename', 'Lat', 'Lon']) # Images with existing GPS
    skipGPS_count = 0

    # Search through folder(s), classify photos as candidates or not
    click.secho(f'\n\nScanning images in {len(folders)} folders . . .',fg = 'yellow')
    for folder in folders:            
        others = 0
        images = 0
        candidates = 0
        withGPS = 0
        no_time = 0  
        failed = 0
        
        for val in folder.iterdir():
            if val.suffix.lower() in formats:
                images += 1
                with open(val, 'rb') as file:

                    try:
                        image = Image(file)
                        if 'datetime_original' in dir(image):
                            check = [tag for tag in gps_tags if tag in dir(image)]
                            if len(check) == 0:
                                attempt[val] = image.get('datetime_original')
                                candidates += 1
                            else:
                                if overwrite:
                                    attempt[val] = image.get('datetime_original')
                                    candidates += 1
                                    skipGPS.loc[skipGPS_count,'Folder'] = folder.name
                                    skipGPS.loc[skipGPS_count,'Filename'] = val.name
                                    if 'gps_latitude' in check:
                                        L = image.get('gps_latitude')                                    
                                        if 'S' in hemi or 'gps_latitude_ref' in check and image.get('gps_latitude_ref') == 'S':
                                            skipGPS.loc[skipGPS_count,'Lat'] = -1*round(L[0]+L[1]/60+ L[2]/3600,6)
                                        else:
                                            skipGPS.loc[skipGPS_count,'Lat'] = round(L[0]+L[1]/60+ L[2]/3600,6)
                                    if 'gps_longitude' in check:
                                        L = image.get('gps_longitude')                                    
                                        if 'W' in hemi or 'gps_longitude_ref' in check and image.get('gps_longitude_ref') == 'W':
                                            skipGPS.loc[skipGPS_count,'Lon'] = -1*round(L[0]+L[1]/60+ L[2]/3600,6)
                                        else:
                                            skipGPS.loc[skipGPS_count,'Lon'] = round(L[0]+L[1]/60+ L[2]/3600,6)   
                                skipGPS_count += 1
                                withGPS += 1
                        else:
                            skiptime.loc[skiptime_count,'Folder'] = folder.name
                            skiptime.loc[skiptime_count,'Filename'] = val.name
                            skiptime_count += 1
                            no_time += 1
                    except Exception as e:
                        click.secho(f'\tFailed loading {folder.name}-{val.name}',fg = 'red')
                        error_report.loc[failed,'Folder'] = folder.name
                        error_report.loc[failed,'Filename'] = val.name
                        error_report.loc[failed,'Error'] = str(e).replace('\n','<br>').replace(' ','&nbsp')
                        failed += 1
                        
            elif val.is_dir() == False:
                others += 1            
        
        available.loc[folder,'Others'] = others
        available.loc[folder,'Images'] = images
        available.loc[folder,'withoutDate'] = no_time
        available.loc[folder,'withGPS'] = withGPS
        available.loc[folder,'Candidates'] = candidates
        available.loc[folder,'Tagged'] = 0
        available.loc[folder,'Failed'] = failed
        available.loc[folder,'OOB'] = 0
    
    if len(attempt) == 0:
         return f"No images to tag in {str(source)}", 'yellow'
    del others, images, candidates, withGPS, no_time, skiptime_count, skipGPS_count
    
    # Source folder contents summary
    click.secho(f'\n\nFound {available.Images.sum()} images',fg = 'yellow')
    click.secho(f'\t{available.withoutDate.sum()} without date taken information',fg = 'magenta')
    click.secho(f'\t{available.withGPS.sum()} with GPS data',fg = 'magenta')
    click.secho(f'\t{available.Failed.sum()} did not load properly',fg = 'magenta')
    click.secho(f'\t{available.Candidates.sum()} to attempt',fg = 'green')

    # Gather candidates into DataFrame
    results = pd.DataFrame(columns = ['filename', 'TZ', 'Date', 'Match', 'delta',\
                                      'accuracy', 'Lat', 'Lon', 'result', 'folder'])  
    for i,[key,val] in enumerate(attempt.items()):
        results.loc[i,'filename'] = key.name
        results.loc[i,'Date'] = val
        results.loc[i,'folder'] = key.parent
    del attempt

    pd.options.mode.chained_assignment = None # suppress SettingWithCopyWarning         
    # TIMEZONE input     
    if timezone == 'prompt':
        tz = False
        while tz == False:
            tzcheck = input('\nSpecify timezone: ')
            try:
                pd.to_datetime(time()*1E9, utc = True).tz_convert(tzcheck)
                results.loc[:,'TZ'] = tzcheck
                click.secho(f'\nTimezone set to {tzcheck}',fg = 'green')
                tz = True
            except Exception as e:
                click.secho(f'\nError reading specified timezone: {tzcheck}',fg = 'yellow')
                click.secho(str(e),fg = 'red')
        del tzcheck, tz
    elif timezone == 'prompt-each':
        for folder in results.folder.unique():
            tz = False
            while tz == False:
                tzcheck = input(f'\nSpecify timezone for {Path(folder).name}: ')
                try:
                    pd.to_datetime(time()*1E9, utc = True).tz_convert(tzcheck)
                    results.loc[results[results.folder == folder].index,'TZ'] = tzcheck
                    click.secho(f'\tTimezone for {Path(folder).name} set to {tzcheck}',fg = 'green')
                    tz = True
                except Exception as e:
                    click.secho(f'\nError reading specified timezone: {tzcheck}',fg = 'yellow')
                    click.secho(str(e),fg = 'red')           
    else:
        results.loc[:,'TZ'] = timezone    
    results['Date'] = pd.to_datetime(results.Date, format = '%Y:%m:%d %H:%M:%S')
    
    timezones = results.TZ.unique()
    if timezones.shape[0] == 1: # Convert if one unique timezone
        results.Date = results.Date.dt.tz_localize(timezones[0])
    else:  # For bulk conversion, mixed timezones must be converted back to UTC
        convert = pd.DataFrame(columns = ['Date'], index = results.index)
        for val in timezones:
            ind = results[results.TZ == val].index
            convert.loc[ind, 'Date'] = results.loc[ind, 'Date'].dt.tz_localize(val)           
        results['Date'] = pd.to_datetime(convert.Date, utc = True)
    
    # Candidate time span
    begin = results.Date.min()
    endin = results.Date.max()
    if results.shape[0] > 1:
        click.secho('\nCandidates span from',fg = 'yellow')
        click.secho(f'{begin.strftime("%x %X %Z")}\nto\n{endin.strftime("%x %X %Z")}',fg = 'green')
    else: 
        click.secho(f'\nCandidate image taken on {begin.strftime("%x %X %Z")}',fg = 'green')
    
    click.secho('Loading + chopping location data . . .',fg = 'yellow')   
    # Data Load
    data = pd.read_parquet(location_data_path, engine='fastparquet')
    data = data.loc[:,['timestamp','accuracy','Lat','Lon']] # remove source, deviceTag, timeStep
    if data.timestamp.dtype != 'datetime64[ns, UTC]':
        data['timestamp'] = pd.to_datetime(data['timestamp'], utc = True) # leave as UTC   
    data.timestamp = data.timestamp.dt.tz_convert(results.Date.dt.tz) 
    
    # Chop data
    MINdex = bisect.bisect_left(data.timestamp, begin)
    MAXdex = bisect.bisect(data.timestamp, endin)+1
    step = pd.Timedelta('3 days') # provide some buffer to chop
    if MINdex == 0:
        early_chop = MINdex
    else:
        if begin - data.timestamp[MINdex-1] > step:
            early_chop = MINdex - 1
        else:
            early_chop = bisect.bisect_left(data.timestamp, begin - step)
    if MAXdex >= data.shape[0]-1:
        late_chop = MAXdex
    else:
        if data.loc[MAXdex+1,'timestamp'] - endin > step:
            late_chop = MAXdex + 1
        else:
            late_chop = bisect.bisect(data.timestamp, endin + step)+1
        
    click.secho(f'\tBefore chop: {data.shape[0]}', fg = 'magenta')
    percentage = round(100*(late_chop - early_chop) / data.shape[0],2)
    data = data.loc[early_chop:late_chop,:].reset_index(drop = True)
    click.secho(f'\tAfter chop: {data.shape[0]} ({percentage}%)', fg = 'magenta')    
    del percentage, MINdex, MAXdex, late_chop, early_chop
    
    # Make folder for copies
    savetime = asctime().replace(":","•")
    savefolder = Path(Path.cwd(),'Outputs',f'geotag_{savetime}')

    if savefolder.exists():
        click.secho('\n\nResults may overwrite previous attempts, target save folder exists:', fg = 'yellow')
        click.secho(click.format_filename(savefolder),fg='blue')
    else:
        savefolder.mkdir()
        click.secho('\n\nSaving results to folder:', fg = 'yellow')
        click.secho(click.format_filename(savefolder),fg='blue')
    
    # Location Matching
    click.secho('\n\nMatching photos to GPS data, saving tagged copies', fg = 'yellow')
    a5 = np.percentile(data.accuracy, q = 50) # median accuracy of chopped data set
    endin = data.timestamp.max()
    begin = data.timestamp.min()
    
    with click.progressbar(results.Date, label='Matching', show_percent=True, 
                           fill_char='■', empty_char = '¤', color = 'cyan') as bar:
        for i,val in enumerate(bar):
            ind = bisect.bisect(data.timestamp, val)
            match = data.loc[ind,:]
            # outside location bounds check
            if (ind == 0 and abs(begin - val) > flag_time) or (ind == data.shape[0]-1 and abs(endin - val) > flag_time):
                results.loc[i,'result'] = 'out of bounds'
                results.loc[i,'Match'] = match.timestamp
                results.loc[i,'delta'] = abs(match.timestamp-val)    
                available.loc[results.loc[i,'folder'],'OOB'] += 1
            else: 
                if abs(match.timestamp - val) > pd.Timedelta('1 min') or match.accuracy > 20: # bigger window to match
                    low = 0 if ind < 5 else ind-5
                    high = data.shape[0]-1 if ind > data.shape[0]-6 else ind+5
                    match = data.loc[low:high,:]
                    match['delta'] = abs(match.timestamp-val)            
                    # Score by timedelta and accuracy            
                    d5 = pd.Timedelta(np.percentile(match.delta, q = 50))
                    for x in match.index:
                        match.loc[x,'score'] = match.loc[x,'accuracy']/a5 + match.loc[x,'delta']/d5             
                    match = match.sort_values('score').iloc[0,:]
        
                results.loc[i,'Match'] = match.timestamp
                results.loc[i,'delta'] = abs(match.timestamp-val)
                results.loc[i,'Lat'] = round(match.Lat*1e-7,7)
                results.loc[i,'Lon'] = round(match.Lon*1e-7,7)
                results.loc[i,'accuracy'] = match.accuracy        
    results.delta = pd.to_timedelta(results.delta)
    results.Match = pd.to_datetime(results.Match)
    
    # Attempt GeoTag for matched images
    failed = 0 # new count for printout
    with click.progressbar(results[results.result.isnull()].index, label='Tagging ', show_percent=True, 
                           fill_char='■', empty_char = '¤', color = 'cyan') as bar:
        for i in bar:
            filename = results.filename[i]
            path = Path(results.folder[i], filename)            
            with warnings.catch_warnings(record = True) as w:
                try:
                    # Open image, write data
                    image = Image(Path(results.folder[i], results.filename[i]))
                    image.gps_latitude, image.gps_latitude_ref = DMS(results.Lat[i],'Lat')
                    image.gps_longitude, image.gps_longitude_ref = DMS(results.Lon[i],'Lon')
                    # Save geocopy in appropriate folder
                    if path.parent != source:
                        if Path(savefolder, path.parent.name).exists() == False:
                            Path.mkdir(Path(savefolder, path.parent.name))
                        with open(Path(savefolder, path.parent.name, filename), 'wb') as image_copy:
                            image_copy.write(image.get_file())
                    else:
                        with open(Path(savefolder, filename), 'wb') as image_copy:
                            image_copy.write(image.get_file())     
                    # Save record
                    results.loc[i,'result'] = 'tagged'
                    available.loc[path.parent,'Tagged'] += 1
                except Exception:
                    if w:
                        results.loc[i,'result'] = f'{str(w[-1].message)}'
                    else:
                        results.loc[i,'result'] = 'error'
                    available.loc[path.parent,'Failed'] += 1
                    failed += 1
        
    # Tagging summary
    click.secho(f'\n\n{available.Candidates.sum()} candidate images:',fg = 'yellow')
    click.secho(f'\t{available.Tagged.sum()} tagged copies created',fg = 'green')
    if failed > 0:
        click.secho(f'\t{failed} tagging attempts failed',fg = 'red')
    if results[results.result == 'out of bounds'].shape[0] > 0:
        click.secho(f'\t{results[results.result == "out of bounds"].shape[0]} outside location data bounds',fg = 'magenta')
    
    # Generate + Style HTML tables for report
    click.secho('\n\nGenerating and saving summary of results', fg = 'yellow')
    available.to_csv(Path(savefolder,'results-summary.csv'))
    
    # Map Results
    if photomap:
        from .mapMe import tagmap
        maplinks = tagmap(results.copy(), skipGPS.copy(), source.name, savefolder)
    else:
        maplinks = None
        
    if not flag_accuracy:
        flag_accuracy = a5    
       
    # Generate + Style HTML tables for report
    if detailed_report:
        geotag_report(savefolder, maplinks, results.copy(), available, flag_accuracy, flag_time, \
                          error_report, skiptime, skipGPS, timezones, overwrite)

    # Offer to open / locate the results
    if open_mode == 'locate':
        click.secho(click.format_filename(savefolder),fg='blue')
        click.secho('\tOpen results folder? (y/n):', fg = 'cyan', nl = False)
        to_open = click.getchar()
        if to_open.lower() == 'y': 
            click.launch(click.format_filename(Path(savefolder, 'results-detailed.html')), locate = True)
    
    elif open_mode == 'launch':
        click.secho(click.format_filename(Path(savefolder, 'results-detailed.html')),fg='blue')
        click.secho('\tOpen results report? (y/n):', fg = 'cyan', nl = False)
        to_open = click.getchar()
        if to_open.lower() == 'y': 
            click.launch(click.format_filename(Path(savefolder, 'results-detailed.html')))    
    
    return '\n\nConcluded GeoTag trial!', 'green'