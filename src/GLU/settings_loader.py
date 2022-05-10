# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 2022

@author: NBPub
"""
from pathlib import Path
from configparser import ConfigParser
from time import time
import click
import pandas as pd

def source_folder(operation):
    source = None    
    while source == None or source.replace(' ','') == '':
        try:
            source = input(f'Choose folder to {operation}: ')
            if source == 'exit':
                return 'exit'
            elif Path(source).exists():
                source = Path(source)
                return source
            else:
                click.secho('Folder not detected',fg = 'red')
                source = None
        except Exception as e:
            click.secho(str(e),fg = 'red')
            source = None

def loc_loader(operation):
    from .filestatus import folder_check
    folder_check()
    
    locfiles = Path(Path.cwd(), 'LocationData').iterdir()
    available = {}
    counter = 1
    
    if operation == 'filtering':
        for file in locfiles:
            if file.suffix == '.parquet' and file.name.startswith('parsed_'):
                available[str(counter)] = file
                counter += 1                
    elif operation == 'reporting':
        for file in locfiles:
            if file.suffix == '.parquet':
                available[str(counter)] = file
                counter += 1
    del locfiles, counter
    
    if len(available) == 0:
        click.secho(f'Location data required for {operation}', fg = 'red')
        return 'abort'
    elif len(available) > 1:
        click.secho('Available location files:', fg = 'magenta')
        for val in available:
            click.secho(f'\t{val}. {available[val].name}', fg = 'blue')        
        choice = input(f'Choose file for {operation}, enter number: ')
        while choice not in available.keys():
            if choice.lower() == 'exit':
                return 'abort'
            click.secho('Invalid selection \n', fg='red')
            choice = input('Choose file to filter, enter number: ')                       
    else:
        choice = '1'
        click.secho('Found one location data file:', fg = 'magenta')
        click.secho(f'{available[choice].name}.', fg = 'blue')
        
    return available[choice]

def loc_loader_config(attempt, operation):
    try:
        attempt = f'{attempt.lower()}.parquet'
        location_data_path =  Path(Path.cwd(), 'LocationData', attempt)
        if location_data_path.exists():
            return location_data_path
        else:
            location_data_path = ''
    except:
        location_data_path = ''
    
    if location_data_path == '':
        from .filestatus import folder_check
        folder_check()
        selection = {}
        counter = 1
        locfiles = Path(Path.cwd(), 'LocationData').iterdir()
        for val in locfiles:
            if val.suffix == '.parquet':
                selection[str(counter)] = val
                counter += 1
        if len(selection) == 0:
            click.secho("No location data available for {operation}", fg = "red")
            return 'abort'
        else:
            click.secho('\nLocation files for map creation:',fg = 'yellow')
            for key,val in selection.items():
                click.secho(f'\t{key}. {val.name}', fg = 'cyan')            
            choice = ''
            while choice not in selection.keys():
                choice = input('Enter file #: ')
                if choice == 'exit':
                    return 'abort'
                try:
                    location_data_path = selection[choice]
                except:
                    click.secho('Invalid selection \n', fg='red')
                    
        return location_data_path

def config_load(section):
    if Path(Path.cwd(), 'Configuration.ini').exists() == False:
        click.secho(f'Configuration settings not found, searching for "Configuration.ini" in "{click.format_filename(Path.cwd())}" directory . . .', 'red')
        exit
    
    config = ConfigParser()
    config.read(Path(Path.cwd(), 'Configuration.ini'))
    
    if section == 'location_report':
        read_settings = [f'{key}={val}' for key,val in config['LocationReport'].items()]
        read_settings = '<br>'.join(read_settings)
        read_settings = f'[LocationReport]<br>{read_settings}'
        # Accuracy Split, default to 565
        try:
            split = abs(config.getint('LocationReport','accuracy_split'))
        except Exception as e:
            click.secho(f'\t\tError reading accuracy_split.\n{str(e)}', fg = 'red')
            split = 565
        # Figure DPI, accept 1-50, default to 20
        try:
            figure_dpi = config.getint('LocationReport','figure_dpi')
            figure_dpi = 300 if figure_dpi > 300 else figure_dpi
            figure_dpi = 100 if figure_dpi < 100 else figure_dpi
        except Exception as e:
            click.secho(f'\t\tError reading figure_dpi.\n{str(e)}', fg = 'red')
            figure_dpi = 100
        # Notable TimeGaps, accept 1-50, default to 20
        try:
            timegaps = config.getint('LocationReport','notable_timegaps')
            timegaps = 50 if timegaps > 50 else timegaps
            timegaps = 1 if timegaps < 1 else timegaps
        except Exception as e:
            click.secho(f'\t\tError reading notable_timegaps.\n{str(e)}', fg = 'red')
            timegaps = 20
        # Device Maps, defaults to True    
        try:
            device_maps = config.getboolean('LocationReport','device_maps')
        except Exception as e:
            click.secho(f'\t\tError reading device_maps.\n{str(e)}', fg = 'red')
            device_maps = True
        
        return read_settings, split, figure_dpi, timegaps, device_maps
        
    elif section == 'location_filter':
        read_settings = [f'\t{key}={val}' for key,val in config['LocationFilter'].items()]
        read_settings = '\n'.join(read_settings)
        click.secho('[LocationFilter]', fg = 'yellow', bg = 'blue')
        click.secho(read_settings, fg = 'yellow', bg = 'blue')
        click.echo('\n\n')
        # Accuracy Cutoff, must be integer
        try:
            cutoff = abs(config.getint('LocationFilter','accuracy_cutoff'))
        except Exception as e:
            click.secho(f'Error reading accuracy_cutoff:\n{str(e)}\n', fg = 'red')
            cutoff = 'abort'
        # Source(s) to remove, must be comma separated.
        if 'remove_sources' in config['LocationFilter'].keys() and config.get('LocationFilter','remove_sources') != '':
            try:
                remove_sources = config.get('LocationFilter','remove_sources').split(',')
            except Exception as e:
                click.secho(f'Error reading remove_sources:\n{str(e)}\n', fg = 'red')
                remove_sources = 'abort'
        else:
            remove_sources = None
        # Device(s) to remove, must be comma separated.
        if 'remove_devices' in config['LocationFilter'].keys() and config.get('LocationFilter','remove_devices') != '':
            try:
                remove_devices =  config.get('LocationFilter','remove_devices').split(',')
            except Exception as e:
                click.secho(f'Error reading remove_devices:\n{str(e)}', fg = 'red')
                remove_devices = 'abort'
        else:
            remove_devices = None       
        return cutoff, remove_sources, remove_devices
    
    elif section =='geoStrip':
        try:
            subfolders = config.getboolean('geoStrip','subfolders')
        except:
            subfolders = True
        try:
            open_mode = config.get('geoStrip','open_mode').lower()
            if open_mode not in ['locate','launch', 'disable']:
                open_mode = 'locate'
        except:
            open_mode = 'locate'    
        return subfolders, open_mode
    
    elif section == 'geoTag':
        read_settings = [f'\t{key}={val}  ' for key,val in config['geoTag'].items()]
        read_settings = '\n'.join(read_settings)
        click.secho('Input Settings:', fg = 'yellow', bg = 'magenta')
        click.secho(read_settings, fg = 'yellow', bg = 'magenta')  

        try: # Subfolders
           subfolders = config.getboolean('geoTag','subfolders')
        except:
           subfolders = True
        try: # Overwrite
            overwrite = config.getboolean('geoTag','overwrite')
        except:
            overwrite = False
        try: # Hemisphere Assumption
            hemi = config.get('geoTag','hemi').upper()
            if len(hemi) > 2:
                hemi == ''
        except:
            hemi = ''       

        # location data
        location_data = config.get('geoTag','location_data')
        location_data_path = loc_loader_config(location_data, 'geoTag operation')
        if type(location_data_path) != type(Path()): 
            click.secho("\nGeoTag operation aborted.", fg = "yellow")
            exit

        try: # timezone
            timezone = config.get('geoTag','timezone')
            timezone = 'prompt-each' if timezone in ['', None] else timezone
            if timezone not in ['prompt', 'prompt-each']:
                try:
                    pd.to_datetime(time()*1E9, utc = True).tz_convert(timezone) # test conversion of dummy time, keep if successful
                except Exception as e:
                    click.secho(f'\nError reading specified timezone: {timezone}',fg = 'yellow')
                    click.secho(str(e),fg = 'red')
                    click.secho('\nTimezone specification will be prompted later.\n',fg = 'yellow')
                    timezone = 'prompt-each'
        except:
            timezone = 'prompt-each'                    
        try: # flag_time
            flag_time = config.get('geoTag','flag_time')
            try:
                flag_time = pd.Timedelta(flag_time)
            except Exception as e:
                click.secho(f'\nError reading specified flag_time: {flag_time}',fg = 'yellow')
                click.secho(str(e),fg = 'red')
                click.secho('\nflag_time specification set to default "1 day"\n',fg = 'yellow')
                flag_time = pd.Timedelta('1 day')               
        except:
            flag_time = pd.Timedelta('1 day')
        try: #flag_accuracy
            flag_accuracy = abs(config.getint('geoTag','flag_accuracy'))
            if flag_accuracy == 0:
                flag_accuracy = None
        except:
            flag_accuracy = None
        try: # HTML Report, yes/no
            detailed_report = config.getboolean('geoTag','detailed_report')
        except:
            detailed_report = True   
        try: # Map
            photomap = config.getboolean('geoTag','results_map')
        except:
            photomap = True
        try: # Open mode
            open_mode = config.get('geoTag','open_mode').lower()
            if open_mode == 'launch' and not detailed_report:
                click.secho('\n"open_mode" set to "locate", cannot "launch" if detailed_report is off. . .\n',fg = 'yellow')
                open_mode = 'locate'
            if open_mode not in ['locate','launch', 'disable']:
                open_mode = 'locate'
        except:
            open_mode = 'locate'      
        click.secho('\nSettings to be applied:', fg = 'magenta', bg='yellow')
        click.secho(f'\tsubfolders={subfolders}  ', fg = 'magenta', bg='yellow')
        click.secho(f'\toverwrite={overwrite}  ', fg = 'magenta', bg='yellow')
        click.secho(f'\themi={hemi}  ', fg = 'magenta', bg='yellow')
        click.secho(f'\tlocation_data={location_data_path.name.replace(location_data_path.suffix,"")}  ', fg = 'magenta', bg='yellow')
        click.secho(click.format_filename(location_data_path),fg = 'blue')        
        click.secho(f'\ttimezone={timezone}  ', fg = 'magenta', bg='yellow')        
        click.secho(f'\tflag_time={flag_time}  ', fg = 'magenta', bg='yellow')        
        click.secho(f'\tflag_accuracy={flag_accuracy}  ', fg = 'magenta', bg='yellow')         
        click.secho(f'\tdetailed_report={detailed_report}  ', fg = 'magenta', bg='yellow')        
        click.secho(f'\tresults_map={photomap}  ', fg = 'magenta', bg='yellow')        
        click.secho(f'\topen_mode={open_mode}  ', fg = 'magenta', bg='yellow') 

        return subfolders, overwrite, hemi, location_data_path, timezone, \
               flag_accuracy, flag_time, detailed_report, open_mode, photomap           

    elif section == 'mapMe':
        # location data
        location_data = config.get('Map','location_data')
        location_data_path = loc_loader_config(location_data, 'map creation')
        if type(location_data_path) == type(Path()):
            click.secho(f'Using {location_data_path.name} for map creation.',fg = 'yellow')  
            click.secho(click.format_filename(location_data_path),fg = 'blue')
        else:
            location_data_path = 'exit'
            return location_data_path, None, None, None, None, None
        
        # timezone
        timezone = config.get('Map','timezone')
        if timezone != '':
            try: 
                pd.to_datetime(time()*1E9, utc = True).tz_convert(timezone) # test conversion of dummy time, keep if successful
                click.secho(f'\nTimezone set to {timezone}',fg = 'green')
                check = True
            except Exception as e:        
                click.secho(f'Error reading specified timezone: {timezone}',fg = 'yellow')
                click.secho(str(e),fg = 'red')
                check = False     
        else:
            check = False
        while check == False:
            timezone =  input('\nSpecify timezone: ')
            try:
                if timezone == 'exit':
                    check = True
                    return location_data_path, timezone, None, None, None, None
                pd.to_datetime(time()*1E9, utc = True).tz_convert(timezone)
                click.secho(f'\nTimezone set to {timezone}',fg = 'green')
                check = True
            except Exception as e:
                click.secho(f'\nError reading specified timezone: {timezone}',fg = 'yellow')
                click.secho(str(e),fg = 'red')  
                check = False
        
        # begin
        begin = config.get('Map','begin').lower()
        if begin != '':
            try: # begin
                begin = pd.Timestamp(begin, tz = timezone).floor('d')
                click.secho(f'\nBegin set to {begin}', fg = 'green')
                check = True
            except:
                click.secho('\n"begin" date not specified or invalid', fg = 'red')
                check = False
        else:
            check = False
        while check == False:
            begin = input('\nEnter start date: ')
            if begin == 'exit':
                check = True
                return location_data_path, timezone, begin, None, None, None
            elif begin == '':
                check = False
            else:
                try:
                    begin = pd.Timestamp(begin, tz = timezone).floor('d')
                    click.secho(f'Begin set to {begin}', fg = 'green')
                    check = True
                except Exception as e:
                    click.secho(f'Invalid selection: {str(e)}\n', fg = 'red')
                    check = False 
        
        # endin
        endin = config.get('Map','endin').lower() 
        if endin != '':
            try: 
                endin = pd.Timestamp(endin, tz = timezone).floor('d')
                click.secho(f'\nEndin set to {endin}', fg = 'green')
                check = True
            except:
                click.secho('\n"endin" date not specified or invalid', fg = 'red')
                check = False
        else:
            check = False     
        while check == False:
            endin = input('\nEnter end date: ')
            if endin == 'exit':
                check = True
                return location_data_path, timezone, begin, endin, None, None
            elif ending == '':
                check = False
            else:
                try:
                    endin = pd.Timestamp(endin, tz = timezone).ceil('d')
                    click.secho(f'Endin set to {endin}', fg = 'green')
                    check = True
                except Exception as e:
                    click.secho(f'Invalid selection: {str(e)}\n', fg = 'red')
                    check = False
                
        try: # open_mode at end of operation
            open_mode = config.get('Map','open_mode').lower()
            open_mode = 'locate' if open_mode not in ['launch','locate','disable'] else open_mode
        except:
            open_mode = 'locate'
        
        # Map Type
        style_by = config.get('Map','style_by').lower()
        while style_by not in ['time','frequency', 'exit']:
            click.secho(f'\nInvalid or not specified "style_by" setting, {style_by}', fg = 'red')
            click.secho('Valid options:',fg = 'yellow')
            click.secho('\ttime\n\tfrequency',fg = 'cyan')
            choice = input('Choose option: ').lower()
            style_by = choice
        
        if style_by != 'exit':
            click.secho(f'\nMapping against {style_by}.', fg = 'green')   
        return location_data_path, timezone, begin, endin, open_mode, style_by