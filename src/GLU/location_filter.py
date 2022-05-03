# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 2022

@author: NBPub
"""

import pandas as pd
from pathlib import Path
from time import time, asctime
import click
from .settings_loader import config_load

def location_filter(data, overwrite):
    # Choose location data, skip if data in memory
    if data is None:
        from .settings_loader import loc_loader
        parse_path = loc_loader('filtering')
        if parse_path == 'abort':
            return "Filter operation aborted", 'yellow'
    elif overwrite and overwrite != 'OW':
        parse_path = overwrite

    # Overwrite check
    if Path(Path.cwd(), 'LocationData', 'filtered.parquet').exists() and overwrite != 'OW':
        click.secho('\nThe following operation will replace existing "filtered.parquet", when complete.\n Continue (y/n)?', fg = 'cyan', nl = False)
        to_overwrite = click.getchar()
        if to_overwrite.lower() != 'y':
            return 'User declined operation', 'yellow'
    elif Path(Path.cwd(), 'LocationData', 'filtered.parquet').exists() and overwrite == 'OW': # Overwrite specified in call
        click.secho('\nSaving over existing "filtered.parquet" . . .', fg = 'yellow')
        pass

    click.secho('\n\nReading Filter Settings. . .\n', fg = 'yellow')  
    # load and read Filter settings, confirm continue
    cutoff, remove_sources, remove_devices = config_load('location_filter')
    if 'abort' in [cutoff, remove_sources, remove_devices]:
       return 'Filter operation aborted', 'magenta'
       
    click.secho('\nContinue with location filter operation? (y/n):', fg = 'cyan', nl = False)
    to_open = click.getchar()
    if to_open.lower() != 'y':
        return "Aborted!", "yellow"
    
    # Begin Filtering operation
    start = time()
    click.secho('\nLoading data, applying filters, saving as "filtered.parquet" in LocationData folder.', fg = 'yellow')    
    data = pd.read_parquet(parse_path, engine = 'fastparquet') if data is None else data
    # Save previous size, observation rate for before/after information
    before = data.shape[0]
    before_end = data.timestamp.max()
    before_start = data.timestamp.min()
    before_ObsRate = 3600*before/(before_end-before_start).total_seconds()
    # Accuracy Cutoff
    hits = data[data.accuracy > cutoff].shape[0]
    data = data[data.accuracy <= cutoff]
    click.secho(f'\t{round(100*hits/before,2)}% entries removed with accuracy > {cutoff}', fg = 'bright_magenta')
    # Remove device(s) by deviceTag
    if remove_devices:
        for val in remove_devices:
            hits = data[data.deviceTag == val.replace(' ','')].index
            data = data.drop(index = hits)
            click.secho(f'\t{round(100*hits.shape[0]/before,2)}% entries removed with deviceTag: {val}', fg = 'bright_magenta')
    # Remove source(s) by source name
    if remove_sources: 
        for val in remove_sources:
            hits = data[data.source == val.replace(' ','')].index
            data = data.drop(index = hits)
            click.secho(f'\t{round(100*hits.shape[0]/before,2)}% entries removed from source: {val}', fg = 'bright_magenta')
    # Reset dtypes, index
    data['source'] = data['source'].astype('str')
    data['source'] = data['source'].astype('category')
    data['deviceTag'] = data['deviceTag'].astype('str')
    data['deviceTag'] = data['deviceTag'].astype('category')
    data.reset_index(drop = True, inplace = True)   
    # Save as parquet
    click.secho('\tSaving data', fg = 'bright_magenta')
    data.to_parquet(Path(Path.cwd(), 'LocationData', 'filtered.parquet'), engine = 'fastparquet')
    # End filter operation
    elapsed = time() - start
    click.secho('\tFinished in {:.2f} seconds \n'.format(elapsed), fg = 'green')
    
    filtered_start = data.timestamp.min()
    filtered_end = data.timestamp.max()
    filtered_ObsRate = 3600*data.shape[0]/(filtered_end - filtered_start).total_seconds()
  
    # Record key information of filter operation
    records_path = Path(Path.cwd(), 'LocationData', 'filter_notes.csv')
    if records_path.exists():
        records = pd.read_csv(records_path, index_col = 0)
        chisel = records.index.max()+1
    else:
        records = pd.DataFrame(columns = ['FilterDate','Operation_Time_s', 'Parent', 'Parent_Records', 'Parent_Obs/Hr', \
                               'Parent_span','Filtered_Records', 'Filtered_Obs/Hr','Filtered_span', 'Drop%', \
                               'Accuracy_Cutoff', 'remove_sources', 'remove_devices', \
                               'Start', 'End'])
        chisel = 1
    
    records.loc[chisel,'FilterDate'] = pd.to_datetime(asctime())
    records.loc[chisel,'Operation_Time_s'] =  round(elapsed,2)
    records.loc[chisel,'Parent'] = parse_path.name
    records.loc[chisel,'Parent_Records'] = before
    records.loc[chisel,'Parent_Obs/Hr'] = round(before_ObsRate,2)
    records.loc[chisel,'Parent_span'] = before_end - before_start
    records.loc[chisel,'Filtered_Records'] = data.shape[0]
    records.loc[chisel,'Filtered_Obs/Hr'] = round(filtered_ObsRate,2)
    records.loc[chisel,'Filtered_span'] = filtered_end - filtered_start
    records.loc[chisel,'Drop%'] = round(100*(1-data.shape[0]/before),2)
    records.loc[chisel,'Accuracy_Cutoff'] = cutoff
    records.loc[chisel,'remove_sources'] = ', '.join(remove_sources) if remove_sources else None
    records.loc[chisel,'remove_devices'] = ', '.join(remove_devices) if remove_devices else None
    records.loc[chisel,'Start'] = filtered_start
    records.loc[chisel,'End'] = filtered_end    
    records.to_csv(records_path)
    
    click.secho('\nNote of filter operation saved:', fg = 'yellow')
    click.secho(f'{click.format_filename(records_path)}\n\n', fg = 'blue')
    
    # Simple printout of filter information
    click.secho(f'Original records: {"{:.3e}".format(before)}\nFiltered records: {"{:.3e}".format(data.shape[0])} ({round(100*data.shape[0]/before,2)}%)\n',\
                fg = 'yellow')
    # Before
    click.secho('\tParsed data:', fg = 'bright_magenta')
    click.secho(click.format_filename(parse_path), fg = 'blue')
    click.secho(f"{before_start.strftime('%x %X')} to {before_end.strftime('%x %X')}", fg = 'yellow')
    click.secho(f"{round(before_ObsRate,2)} records / hour\n\n", fg = 'yellow')
    # After
    click.secho('\tFiltered data:', fg = 'bright_magenta')
    click.secho(click.format_filename(Path(Path.cwd(), 'LocationData', 'filtered.parquet')), fg = 'blue')
    click.secho(f"{filtered_start.strftime('%x %X')} to {filtered_end.strftime('%x %X')}", fg = 'yellow')
    click.secho(f"{round(filtered_ObsRate,2)} records / hour\n", fg = 'yellow')
    
    # Option to generate report
    click.secho('\n\nGenerate report from filtered data? (y/n):', fg = 'cyan', nl = False)
    to_open = click.getchar()
    if to_open.lower() == 'y':
        from .location_report import location_report
        message, color = location_report(data, 'filtered-data')
        click.secho(message, fg = color)

    return '\nLocation data filtered.', 'green'

if __name__ == "__main__":
    pass