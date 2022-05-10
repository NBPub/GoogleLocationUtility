# -*- coding: utf-8 -*-
"""
Created on Tue Apr 5 2022

@author: NBPub
"""

from pathlib import Path
from .settings_loader import config_load
from time import time, asctime
import bisect
import click

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

# Map for geoTag operation
def tagmap(results, GPS, name, savefolder):
    # List of paths to maps, to link in detailed report. One map per 22 photos.
    maplinks = [] 
    
    # Prepare Data for Mapping
    results.Lat = results.Lat.astype('float')
    results.Lon = results.Lon.astype('float')
    results.accuracy = results.accuracy.astype('int')
    hovertimes = [val.tz_convert(results.TZ[i]).strftime('%x %X %Z') for i,val in enumerate(results.Date)] # pretty time for hover label
    results.loc[:,'Match'] = [f"{val.tz_convert(results.TZ[i]).strftime('%x %X %Z')}<br>({results.Lat[i]}, {results.Lon[i]}), Accuracy: {results.accuracy[i]}"\
                  for i,val in enumerate(results.Match)] # match information for hover label
    results.loc[:,'folder'] = [val.name for val in results.folder] # folder name
    
    maptitle = f'<b>Photomap: {name}</b><br>\
               {results.Date.min().strftime("%x %Z")} to {results.Date.max().strftime("%x %Z")}'   
    
    # Gather existing GPS Data (photo already tagged)
    if not GPS.empty:
        # Prism cmap with reduced opacity
        linecolors = [val.replace('rgb','rgba').replace(')',', 0.3)') for val in  px.colors.qualitative.Prism]     
        # Don't plot lines for photos not tagged, else label old GPS "A"
        drop = []
        add = pd.DataFrame(columns = ['Folder','Filename','Lat','Lon','Tag'])
        GPS.loc[:,'Tag'] = 'A'
        for i,val in enumerate(GPS.Filename):
            if val in results.filename.values and (results.loc[np.where(results.filename == val),'result'] == 'tagged').bool(): # "add" new tag information as "B"
                add.loc[i,'Folder'] = GPS.loc[i,'Folder']
                add.loc[i,'Filename'] = GPS.loc[i,'Filename']
                add.loc[i,'Lat'] = results.loc[np.where(results.filename == val),'Lat'].values[0]
                add.loc[i,'Lon'] = results.loc[np.where(results.filename == val),'Lon'].values[0]
            else:
                drop.append(i)           
        add.loc[:,'Tag'] = 'B'
        GPS.drop(index = drop)
        lines = pd.concat([GPS,add])
    else:
        lines = GPS

    # Plot map for every 22 photos, 2 revolutions of the color map.
    for i in range(results.shape[0] // 22 +1):
        start = i*22
        stop = (i+1)*22 if (i+1)*22 <= results.shape[0] else results.shape[0]
        sub = results.iloc[start:stop,:]
        # Marker Map for Tags
        max_bound = max(abs(sub.Lat.max()-sub.Lat.min()), abs(sub.Lon.max()-sub.Lon.min())) * 111.1111
        zoom = 12.5 - np.log(max_bound) if max_bound > 0 else 13
        fig1 = px.scatter_mapbox(sub, lat = 'Lat', lon = 'Lon', color = 'filename',
                                 color_discrete_sequence = px.colors.qualitative.Prism,
                                 hover_name = 'filename', zoom=zoom,  title = maptitle,
                             hover_data = {'filename':False,'Lat':False, 'Lon':False, 'Match':False, 'folder':True,
                                           'TZ':False, 'Date':False, 'delta':False, 'accuracy':False,
                                           'Date Taken':(True,hovertimes[start:stop]), 'Match Data': (True, sub.Match)})
        fig1.update_traces(marker={'allowoverlap':True}, marker_size = 18, marker_opacity=0.7)
        fig1.update_layout(mapbox_style='open-street-map', title_xanchor="center", title_x=0.5, title_y=0.98)
        
        # Line Map for GPS discrepancies
        if not lines.empty:
            subline_ind = []
            for val in sub.filename:
                subline = lines[lines.Filename == val].index
                for ind in subline:
                    subline_ind.append(ind)
            subline = lines.loc[subline_ind,:]
            if not subline.empty:                          
                max_bound = max(abs(subline.Lat.max()-subline.Lat.min()), abs(subline.Lon.max()-subline.Lon.min())) * 111.1111
                zoom = 12.5 - np.log(max_bound) if max_bound > 0 else 13
                fig2 = px.line_mapbox(subline, lat = 'Lat', lon = 'Lon', color = 'Filename', title = maptitle,
                                      zoom = zoom, line_group = 'Filename',  hover_name = 'Filename',
                                      color_discrete_sequence = linecolors,
                                      hover_data = {'Folder':True,'Lat':True,'Lon':True,'Tag':False, 'Filename':False})
                fig2.update_traces({'line_width':5})
                fig2.update_layout(mapbox_style='open-street-map', title_xanchor="center", title_x=0.5, title_y=0.98)
            else:
                fig2 = None
        else:
            fig2 = None
        # Combine plots, if applicable
        if not fig2:
            fig = {"data": [val for val in fig1['data']], "layout": fig1['layout']}
        else: # combine plots
            fig = {
                "data": [val for val in fig2['data']] + [val for val in fig1['data']],
                "layout":  fig1['layout']
            }            
        # Save map as html, keep link in list to return
        saveas = Path(savefolder, f'photomap_{i+1}.html')
        pio.write_html(fig,saveas)
        maplinks.append(saveas)
    return maplinks

# Time Map for location map
def timemap(chop, begin, endin, timezone, ):
    pd.options.mode.chained_assignment = None # suppress SettingWithCopyWarning  
    click.secho('\nGenerating time map . . .', fg = 'magenta')
    
    # Determine length of time periods to gather, based on total time span
    span = chop.timestamp.max() - chop.timestamp.min()
    splinters = {'1h': '15sec', '1 day': '5m', '1W':'15m', '6W':'1h', '12W':'3h', '26W':'6h'}    
    if span > pd.Timedelta('26W'):
        splinter = '12h'
    else:
        for limit, splinter in splinters.items():
            if span < pd.Timedelta(limit):
                break  
    splinter = pd.Timedelta(splinter)
    click.secho(f'\tTime span: {span},\n\tsplitting into {splinter} periods',fg = 'yellow') 
    periods = pd.period_range(begin,endin,freq = splinter) 
    # Gather best location record for each period
    gather = pd.DataFrame(columns = ['Lat','Lon','Acc'])
    for i,val in enumerate(periods):       
        a = chop[(chop.timestamp > val.start_time.tz_localize(timezone)) & (chop.timestamp < val.end_time.tz_localize(timezone))]
        marker =  val.start_time.tz_localize(timezone) + pd.Timedelta(val.freq)/2    
        if a.empty:    
            gather.loc[marker,'Lat'] = None
            gather.loc[marker,'Lon'] = None 
            gather.loc[marker,'Acc'] = None 
        elif a.accuracy.max() != a.accuracy.min():    
            if a.accuracy.median() == a.accuracy.min():
                a = a[a.accuracy <= a.accuracy.median()]
            else:
                a = a[a.accuracy < a.accuracy.median()]
            b = pd.DataFrame(a.value_counts(subset = ['Lat','Lon','accuracy']), columns = ['hits'])
            coords = b.index[0]
            gather.loc[marker,'Lat'] = coords[0]
            gather.loc[marker,'Lon'] = coords[1]
            gather.loc[marker,'Acc'] = coords[2]
        else:
            gather.loc[marker,'Lat'] = round(a.Lat.mean(),6)
            gather.loc[marker,'Lon'] = round(a.Lon.mean(),6)
            gather.loc[marker,'Acc'] = int(a.accuracy.mean())
    # Adjust data for plotting
    del a, chop, splinter, periods
    gather.dropna(inplace = True)
    gather = gather.reset_index().rename(columns = {'index':'t'})
    gather.Lat = gather.Lat.astype('int')*1e-7
    gather.Lon = gather.Lon.astype('int')*1e-7
    gather.Acc = gather.Acc.astype('int')
            
    # Map Setup   
    # Format Time, timezone and then strings for data labels
    gather.t = gather.t.dt.tz_convert(tz = timezone)
    gather['time'] = [val.strftime('%x %X %Z') for val in gather.t]
    maptitle = f'<b>Time Map:</b><br>{begin.strftime("%x")} to {endin.strftime("%x %Z")}<br>{gather.shape[0]} locations'
    # Columns for styling
    gather['colorer'] = pd.Series(gather.t.astype('int64')/1e11).astype('int')
    gather['sizer'] = pd.Series((1/gather.Acc)**-0.3).astype('float')
    gather['filler'] = pd.Series((1/gather.Acc)**0.15).astype('float')
    # Colorbar labels
    cbartimes = [gather.time[0], gather.t.median().strftime('%x %X %Z'), gather.iloc[-1]['time']]
    cbartimes = [f'<b>{val}<b>' for val in cbartimes] # embolden, done with label prefix and suffix in frequency plot
    # Zoom Setting
    max_bound = max(abs(gather.Lat.max()-gather.Lat.min()), abs(gather.Lon.max()-gather.Lon.min())) * 111.1111
    zoom = 13 - np.log(max_bound)
    del max_bound
    # Make Map, return figure
    fig = px.scatter_mapbox(gather, lat = 'Lat', lon = 'Lon', color = 'colorer', color_continuous_scale=px.colors.sequential.Sunset,\
                         size = 'sizer', opacity = gather.filler, title = maptitle, hover_name = 'time', zoom=zoom,
                         hover_data = {'colorer':False,'sizer':False, 't':False, 'Acc':True}) # could use 't':'|%x %X', but d3 format doesn't show timezone   
    
    fig.update_layout(title_xanchor="center", title_x=0.5, title_y=0.98, mapbox_style='open-street-map',
                      coloraxis_colorbar = dict(
                        title = '', thickness = 20, 
                        tickmode = 'array', 
                        tickvals = [gather.colorer.min(), gather.colorer.mean(), gather.colorer.max()], 
                        ticktext = cbartimes,
                        tickfont = dict(family='Old Standard TT', size = 16),
                      ))                                        
    return fig

# Frequency Map for location map, and location report device maps
def freqmap(sourcedata, maptitle):
    pd.options.mode.chained_assignment = None # suppress SettingWithCopyWarning  
    click.secho('\nGenerating frequency map . . .', fg = 'magenta') 
    
    # Round to hundreth degree, then gather value counts for Frequency rating
    sourcedata.Lat = round(sourcedata.Lat*1e-7,2)
    sourcedata.Lon = round(sourcedata.Lon*1e-7,2)        
    gather = pd.DataFrame(sourcedata.value_counts(subset = ['Lat','Lon'], normalize = True)).reset_index()      
    click.secho(f'\tTime span: {sourcedata.timestamp.max() - sourcedata.timestamp.min()}\nLocations: {gather.shape[0]}',fg = 'yellow')  
    # Log-ish distribution for "Frequency" ranking. Keeps low points visible.
    gather['Frequency'] = np.log(gather[0])+(-1.01*np.log(gather[0].min()))
    gather.drop(columns = 0, inplace=True)
    gather.sort_values('Frequency', inplace = True)       
    # Zoom Setting, Maptitle
    max_bound = max(abs(gather.Lat.max()-gather.Lat.min()), abs(gather.Lon.max()-gather.Lon.min())) * 111.1111
    zoom = 12.2 - np.log(max_bound)
    maptitle = f'{maptitle}<br>{gather.shape[0]} locations'
    del max_bound, sourcedata
    # Create Map, return figure
    fig = px.scatter_mapbox(gather, lat = 'Lat', lon = 'Lon', size = 'Frequency', title = maptitle,
                    color = 'Frequency', opacity = np.sqrt(gather.Frequency/gather.Frequency.max()), zoom=zoom,
                    color_continuous_scale=["DeepSkyBlue", "BlueViolet", "DarkMagenta"],
                    hover_data={'Frequency':':.2f'})
    
    fig.update_layout(title_xanchor="center", title_x=0.5, title_y=0.98, mapbox_style='open-street-map',
                      coloraxis_colorbar = dict(
                        title = 'Frequency', thickness = 20, 
                        tickmode = 'array', ticklabelposition='outside bottom',
                        tickvals = [round(val,1) for val in [(gather.Frequency.min()+gather.Frequency.max())/4, (gather.Frequency.min()+gather.Frequency.max())/2, 3*(gather.Frequency.min()+gather.Frequency.max())/4,]],
                        showtickprefix = 'all', showticksuffix = 'all',  tickprefix = '<b>', ticksuffix = '</b>',
                        tickfont = dict(family='Old Standard TT', size = 16),
                      ))  
    return fig

# Location Map function, chop data to specified date-range, then send to appropriate map style
def mapMe():
    # Read settings
    location_data_path, timezone, begin, endin, open_mode, style_by = config_load('mapMe')
    if 'exit' in [location_data_path, timezone, begin, endin, open_mode, style_by]:
        return "Aborted!", "yellow"
    elif None in [location_data_path, timezone, begin, endin, open_mode, style_by]:
        return "Aborted!", "yellow"    
    
    # Load Data
    start = time()
    click.secho('\nLoading data file. Chopping to selected time bounds . . .', fg = 'yellow')    
    data = pd.read_parquet(location_data_path, engine='fastparquet')
    data = data.loc[:,['timestamp','accuracy','Lat','Lon']] # remove source, deviceTag, timeStep
    data.timestamp = data.timestamp.dt.tz_convert(timezone)
    # Chop into specified timeframe
    MINdex = bisect.bisect_left(data.timestamp, begin)
    MAXdex = bisect.bisect(data.timestamp, endin)
    chop = data.iloc[MINdex:MAXdex,:]
    del data
    if chop.empty:
        return "No location data in selected bounds", "red"   
    
    # Create Map     
    if style_by == 'time': # Split into periods, gather location data for each period
        fig = timemap(chop, begin, endin, timezone)        
    elif style_by == 'frequency':
        maptitle = f'<b>Frequency Map:</b><br>{begin.strftime("%x")} to {endin.strftime("%x %Z")}'
        fig = freqmap(chop, maptitle)
        
    # Save in Outputs/Maps
    savefolder = Path(Path.cwd(), 'Outputs', 'Maps')
    if not savefolder.exists():
        savefolder.mkdir()
    savetime = asctime().replace(":","•")
    fig.write_html(Path(savefolder,f'MAP-{style_by}_{savetime}.html'))
    
    elapsed = time() - start
    click.secho('Finished in {:.2f} seconds \n\n'.format(elapsed), fg = 'green') 
    
    # Offer to open / locate the results
    if open_mode == 'locate':
        click.secho(click.format_filename(savefolder),fg='blue')
        click.secho('\tOpen map folder? (y/n):', fg = 'cyan', nl = False)
        to_open = click.getchar()
        if to_open.lower() == 'y': 
            click.launch(click.format_filename(Path(savefolder,f'MAP-{style_by}_{savetime}.html')), locate = True)
    
    elif open_mode == 'launch':
        click.secho(click.format_filename(Path(savefolder,f'MAP-{style_by}_{savetime}.html')),fg='blue')
        click.secho('\tOpen map in HTML browser? (y/n):', fg = 'cyan', nl = False)
        to_open = click.getchar()
        if to_open.lower() == 'y': 
            click.launch(click.format_filename(Path(savefolder,f'MAP-{style_by}_{savetime}.html')))       
    return "\n\nMap created!", "green"