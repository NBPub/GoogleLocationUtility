# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 2022

@author: NBPub
"""

import pandas as pd
import json
from pathlib import Path
from time import time, asctime
import click

def location_parse(folder, file):
    # Data Load
    start = time()
    click.secho('Reading location data into DataFrame. Preparing columns. \n\t', fg = 'yellow', nl = False)
    click.secho('.•.•.•', fg = 'bright_magenta', bold = True)
    with open(Path(folder, file)) as reader:
        data = json.load(reader)
    del reader    
    data = pd.DataFrame.from_dict(data['locations'])
    elapsed = time() - start
    click.secho('\tFinished in {:.2f} seconds \n\n'.format(elapsed), fg = 'green')
    # Data Clean
    start = time()
    click.secho('Cleaning data, calculating time difference between each record \n\
                Saving parsed data as Parquet. \n\t', fg = 'yellow', nl = False)  
    click.secho('.•.•.•', fg = 'bright_magenta',  bold = True)                    
    # keeping: latitude, longitude, accuracy, source, deviceTag, timestamp
    keep = ["latitudeE7", "longitudeE7", "accuracy", "source", "deviceTag", "timestamp"]
    trash = [val for val in list(data.columns) if val not in keep]
    data.drop(columns = trash, inplace = True)   
    # remove negative accuracy values 
    data = data[data.accuracy>0]
    # Combine sources split by capitilization, e.g. "wifi" and "WIFI"
    for val in data.source.unique():
        if val.upper() != val:
            data.loc[data[data.source == val].index, 'source'] = val.upper()    
    # Categorize deviceTag, source
    data['source'] = data['source'].astype('category')
    data['deviceTag'] = data['deviceTag'].astype('str') # categories as strings, not integers, for Basic Report plots
    data['deviceTag'] = data['deviceTag'].astype('category')   
    # Lat, Lon, Accuracy to int
    data['latitudeE7'] = data['latitudeE7'].astype('int')
    data['longitudeE7'] = data['longitudeE7'].astype('int')
    data.rename(columns = {'latitudeE7':'Lat', 'longitudeE7':'Lon'}, inplace = True)
    data['accuracy'] = data['accuracy'].astype('int')
    # Datetime
    data['timestamp'] = pd.to_datetime(data['timestamp'])    
   
    # timeStep, array based calculation. Copy and Shift timestamps for delta between each point
    copy = pd.DataFrame(data.timestamp)
    copy.loc[0,'shift'] = None
    copy.iloc[1:,1] = copy.iloc[:-1,0]    
    data.loc[0,'timeStep'] = None
    copy['shift'] = pd.to_datetime(copy['shift'])
    data['timeStep'] = pd.to_timedelta(data['timeStep'])
    data.loc[1:,'timeStep'] = copy.timestamp[1:] - copy['shift'][1:]
    del copy
    
    # Data Save
    savetime = asctime().replace(":","•")
    data.to_parquet(Path(folder, f'parsed_{savetime}.parquet'), engine = 'fastparquet')
    elapsed = time() - start
    click.secho('\tFinished in {:.2f} seconds \n'.format(elapsed), fg = 'green')
    click.secho('Parsed location data:',fg='yellow')
    click.secho(click.format_filename(Path(folder, f'parsed_{savetime}.parquet'))+'\n\n',fg='blue') 

    # Options to generate report, filter data    
    click.secho('Generate report from parsed data? (y/n):', fg = 'cyan', nl = False)
    to_open = click.getchar()
    if to_open.lower() == 'y':
        from .location_report import location_report
        message, color = location_report(data, f'bulk_{savetime}')
        click.secho(message, fg = color)
    
    click.secho('\n\nFilter parsed data? (y/n):', fg = 'cyan', nl = False)
    to_open = click.getchar()
    if to_open.lower() == 'y':       
        from .location_filter import location_filter
        message, color = location_filter(data,Path(folder, f'parsed_{savetime}.parquet'))
        click.secho(message, fg = color)   


if __name__ == "__main__":
    pass