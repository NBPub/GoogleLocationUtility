# -*- coding: utf-8 -*-
"""
Created on Fri May 04 2022

@author: NBPub
"""

import pandas as pd
import numpy as np
from pathlib import Path
import click

def geotag_report(savefolder, maplinks, results, available, flag_accuracy, flag_time, \
                  error_report, skiptime, skipGPS, timezones, overwrite):
    
    click.secho('\tGenerating detailed report', fg = 'yellow')

    results.Date = results.Date.astype('object')
    for val in results.index:
        results.loc[val,'Date'] = results.loc[val,'Date'].tz_convert(results.loc[val,'TZ'])
    
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
        if maplinks:
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
            # Convert back to input timezone from UTC, if multiple timezones used.
            if timezones.shape[0] > 1:
                TZ = table.TZ.unique()[0]
                if not str(table.Date.dtype).startswith('datetime64'):
                    table['Date'] = pd.to_datetime(table['Date'])
                elif not str(table.Match.dtype).startswith('datetime64'):
                    table['Match'] = pd.to_datetime(table['Match'])                  
                table.Date = table.Date.dt.tz_convert(TZ)
                table.Match = table.Match.dt.tz_convert(TZ)
            # Drop TZ (already on dates), folder (one for each table)
            table.drop(columns = ['TZ', 'folder'], inplace = True)
            table.delta = table.delta.round('s') # round timedelta
            table.Lat = [f"{table.loc[val,'Lat']},{table.loc[val,'Lon']}" for val in table.index] # combine coordinates to one column Lat,Lon
            table.Lon = [f"<a href='{url}{table.loc[val,'Lat']}/'>&#9978;</a>" if table.loc[val,'Lat'] != 'nan,nan' else '' for val in table.index] # Use coordinates to make MapLink column.           
            # Adjust Coordinates, Maplink for photos with existing GPS
            for i in table.index:
                val = table.loc[i,'filename'] 
                old = skipGPS[skipGPS.Filename == val]
                if not old.empty and table.loc[i,'Lon'] != '':
                    GPS = f"{old.Lat.values[0]},{old.Lon.values[0]}"
                    table.loc[i,'Lon'] = f"<a href='{url2}{GPS}/{table.loc[i,'Lat']}/'>&#9978;&#9978;</a>" # MapLink to directions, two house icons
                    if overwrite: # bold persisting tag
                        table.loc[i,'Lat'] = f"<b>B:{table.loc[i,'Lat']}</b> <br><br>A: {GPS}"
                    else:
                        table.loc[i,'Lat'] = f"B:{table.loc[i,'Lat']} <br><br><b>A: {GPS}</b>"
                else:
                    table.loc[i,'Lat'] = f"<b>{table.loc[i,'Lat']}</b>"
                    
            table.Lat = [', <br>'.join(val.split(',')) for val in table.Lat] # space out coordinates
            table.rename(columns = {"Lat":"Coordinates","Lon":"Map Link"}, inplace = True) # rename columns to reflect adjustments  
            # Images to Table
            for i in table.index:
                table.loc[i,'picture'] = f'<img src="{Path(folder,table.loc[i,"filename"])}" \
                                         alt="{table.loc[i,"filename"]}" height="110">' # could do width = 210 for bigger pics/table
            # style and write html
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