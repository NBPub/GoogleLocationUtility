# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 2022

@author: NBPub
"""

import pandas as pd
import click
from .location_report import location_report
from .settings_loader import loc_loader

def create_location_report():
    # Prepare available location files, Choose one to report on
    location_data = loc_loader('reporting')
    if location_data == 'abort':
        return    
    click.secho(location_data, fg = 'magenta')

    # Determine filetype and savelocation
    name = location_data.name
    if name.startswith('parsed_'):
        savetime = name[name.find('_')+1:name.find('.')]
        loctype = f'bulk_{savetime}'
    elif name == 'filtered.parquet':
        loctype = 'filtered-data'    
    else:
        click.secho('Invalid location data filename.', fg = 'red')
        return 

    # Load file, generate report    
    click.secho('Loading data file.\n', fg = 'yellow')
    data = pd.read_parquet(location_data, engine = 'fastparquet')        
    message, color = location_report(data, loctype)
    del data
    click.secho(message, fg = color)
    
if __name__ == "__main__":
    pass
