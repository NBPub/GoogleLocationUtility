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
    
    # source = None    
    # while source == None:
        # try:
            # source = input('Choose folder to geotag: ')
            # if source == 'exit':
                # return 'Aborted!', 'yellow'
            # elif Path(source).exists():
                # source = Path(source)
            # else:
                # click.secho('Folder not detected',fg = 'red')
                # source = None
        # except Exception as e:
            # click.secho(str(e),fg = 'red')
            # source = None
            

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
        if data.timestamp[MINdex] - data.timestamp[MINdex-1] > step:
            early_chop = MINdex - 1
        else:
            early_chop = bisect.bisect_left(data.timestamp, begin - step)
    if MAXdex >= data.shape[0]-1:
        late_chop = MAXdex
    else:
        if data.loc[MAXdex+1,'timestamp'] - data.loc[MAXdex,'timestamp'] > step:
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
       
    # Detailed Report, should move to a separate function
    if detailed_report:
        results.Date = results.Date.astype('object')
        for val in results.index:
            results.loc[val,'Date'] = results.loc[val,'Date'].tz_convert(results.loc[val,'TZ'])
        
        if not flag_accuracy:
            flag_accuracy = a5
        
        shade_cols = {'Images': 'background-color:beige;', \
                      'withoutDate': 'background-color:peru; color:azure;', \
                      'withGPS': 'background-color:peru; color:azure;', \
                      'Candidates': 'background-color:azure; color:green', \
                      'Tagged': 'background-color:darkgreen; color:beige', \
                      'Failed': 'background-color:crimson; color:beige', \
                      'OOB': 'background-color:moccasin; color:darkorchid'}
    
        url = 'https://google.com/maps/search/'
        url2 = 'https://google.com/maps/dir/'
        highlight_result = {'tagged': 'background-color: darkgreen; color: beige; font-weight:bold', \
                            'out of bounds': 'background-color: moccasin; color:darkorchid; font-weight:bold'}
            
        with open(Path(savefolder, 'results-detailed.html'), mode = 'w') as report:
            # Available Table - Top Level Summary
            report.write('<h1>Summary</h1> <br>')
            report.write(available.style\
                         .apply(lambda s: [shade_cols[s.name]] * len(s) if s.name in shade_cols.keys() else ['']*len(s))
                         .applymap(lambda s: 'background-color:grey', subset = 'Others')
                         .set_properties(**{'border':'2px solid midnightblue', 'padding':'5px',\
                                'font-weight':'bold', 'font-size':'large', 'text-align':'center'})
                         .applymap(lambda v: 'background-color:white; color:white; border: 2px whitesmoke' if v == 0 else '')
                         .to_html().replace("</style>",".row_heading {text-align: left;}</style>"))
            
            # Results Table(s) by Folder - Detailed Summary   
            report.write('<hr><br><h1>Results</h1>')
            if photomap:
                report.write('<b>Photomap(s): </b><br>')
                for maplink in maplinks:
                    report.write(f'<a href="{maplink}">{maplink}</a><br>')
                report.write('<br>Markers indicate matched locations. If an image had GPS data, a line is drawn from its existing tag to the matched location.\
                             A maximum of 22 photos are saved on a map.<br><br>')
            
            for folder in results.folder.unique():
                report.write(f'<h2>{Path(folder).name}</h2> <b>{click.format_filename(folder)}</b><br>')
                
                # List images that failed to load
                if error_report[error_report.Folder == Path(folder).name].shape[0] > 0:
                    errors = error_report[error_report.Folder == Path(folder).name]
                    bullets = ''
                    for val in errors.index:
                        bullets += f"<li><b>{errors.loc[val,'Filename']}:</b>{errors.loc[val,'Error']}<br><br></li>"  
                    report.write(f'<h3>Loading Failure</h3><tt><ul>{bullets}</ul></tt>')
                    del errors
                
                # List skipped images due to no time / having GPS
                if skiptime[skiptime.Folder == Path(folder).name].shape[0] > 0:
                    bullets = ''
                    for val in skiptime[skiptime.Folder == Path(folder).name].Filename:
                        bullets += f'<li style="font-weight:bold;"> {val}</li>'
                    report.write(f'<h3>No Time</h3><ul>{bullets}</ul>')
                
                # List Photos with GPS Tags
                if skipGPS[skipGPS.Folder == Path(folder).name].shape[0] > 0:
                    bullets = ''
                    for val in skipGPS[skipGPS.Folder == Path(folder).name].Filename:
                        bullets += f'{val}, '
                    report.write(f'<h3>GPS Tagged</h3><ul><li style="font-weight:bold;">{bullets}</li></ul>')
                    report.write('<br>Existing photo locations are listed as <b>A</b> in the table, newly matched locations are listed as <b>B</b>, \
                    and bold text represents the applied <b>geoTag.</b><br> A/B correspond to the start and stop locations in the map link.')
                  
                    
                table = results[results.folder == folder]
                # Convert back to input timezone from UTC, if multiple timezones used
                if timezones.shape[0] > 1:
                    TZ = table.TZ.unique()[0]
                    if not str(table.Date.dtype).startswith('datetime64'):
                        table['Date'] = pd.to_datetime(table['Date'])
                    elif not str(table.Match.dtype).startswith('datetime64'):
                        data['Match'] = pd.to_datetime(data['Match'])                  
                    table.Date = table.Date.dt.tz_convert(TZ)
                    table.Match = table.Match.dt.tz_convert(TZ)
                
                table.drop(columns = ['TZ', 'folder'], inplace = True)
                table.delta = table.delta.round('s')
                table.Lat = [f"{table.loc[val,'Lat']},{table.loc[val,'Lon']}" for val in table.index]
                table.Lon = [f"<a href='{url}{table.loc[val,'Lat']}/'>&#9978;</a>" if table.loc[val,'Lat'] != 'nan,nan' else '' for val in table.index]                
                # ADJUST Lon column for entries with existing GPS data (skipGPS)
                for i in table.index:
                    val = table.loc[i,'filename'] 
                    old = skipGPS[skipGPS.Filename == val]
                    if not old.empty and table.loc[i,'Lon'] != '':
                        GPS = f"{old.Lat.values[0]},{old.Lon.values[0]}"
                        table.loc[i,'Lon'] = f"<a href='{url2}{GPS}/{table.loc[i,'Lat']}/'>&#9978;&#9978;</a>"
                        if overwrite:
                            table.loc[i,'Lat'] = f"<b>B:{table.loc[i,'Lat']}</b> <br><br>A: {GPS}"
                        else:
                            table.loc[i,'Lat'] = f"B:{table.loc[i,'Lat']} <br><br><b>A: {GPS}</b>"
              
                table.Lat = [', <br>'.join(val.split(',')) for val in table.Lat]
                table.rename(columns = {"Lat":"Coordinates","Lon":"Map Link"}, inplace = True)               
                # Images to Table
                for i in table.index:
                    table.loc[i,'picture'] = f'<img src="{Path(folder,table.loc[i,"filename"])}" \
                                             alt="{table.loc[i,"filename"]}" height="110">' # could do width = 210 for bigger pics/table
                
                report.write(table.style.applymap(lambda v: highlight_result[v] if v in highlight_result.keys() \
                                                else 'background-color:crimson;color:beige;font-weight:bold', subset = 'result')
                           .format(lambda t: t.strftime('%x %X %Z'), subset = ['Date','Match'])
                           .format(lambda t: '' if t in [np.nan,'nan, <br>nan'] else t, subset = ['accuracy', 'Coordinates'])
                           .applymap(lambda s: 'background-color:beige', subset = ['Date','Match'])
                           .applymap(lambda s: 'background-color:bisque; color:indigo;', subset = ['Coordinates','Map Link'])
                           .applymap(lambda v: 'background-color:lightpink' if v > flag_time else 'background-color:darkseagreen', subset = 'delta')
                           .applymap(lambda v: 'background-color:lightpink' if v > flag_accuracy else 'background-color:darkseagreen', subset = 'accuracy')
                           .set_properties(**{'border':'2px solid midnightblue', 'padding':'5px',\
                                              'text-align':'center'}).hide(axis='index')
                           .to_html(na_rep='')) 
                report.write('<hr><br><br>')

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
    
