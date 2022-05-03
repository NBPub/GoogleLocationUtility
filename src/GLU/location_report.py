# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 2022

@author: NBPub
"""

import json
from pathlib import Path
from shutil import rmtree
from time import time
import click
from .settings_loader import config_load
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def location_report(data, report_name):
    # Folder for report
    report_folder = Path(Path.cwd(),'Outputs',f'LocationReport_{report_name}')    

    # Existing Report Folder check
    if report_folder.exists():
        click.secho('Location Report for filtered data exists!', fg = 'yellow')
        click.secho(f'{click.format_filename(report_folder)}\n', fg = 'blue')
        click.secho('\t"r" Rename, choose new report folder name. \
                     \n\t"o" Overwrite existing report folder.', fg = 'cyan')   
        choice = input('Choose option: ')
        while choice.lower() not in ['o','r', 'exit', 'rename', 'overwrite']:
            click.secho('Invalid selection \n', fg='red')
            choice = input('Choose option: ')
        
        if choice.lower() in ['o', 'overwrite']:
            rmtree(report_folder, ignore_errors = True)
   
        elif choice.lower() in ['r', 'rename']:
            taken = [val.name.replace("LocationReport_","")\
                     for val in Path(Path.cwd(),'Outputs').iterdir() \
                         if val.is_dir() and val.name.startswith('LocationReport_')]
            click.secho('\nExisting Location report, ensure new name is not in list:', fg = 'yellow')
            click.secho(', '.join(taken), fg = 'cyan')
            click.echo()
            change_name = input('Enter new name for existing folder: LocationReport_')
            while change_name in taken:
                click.secho('Name not unique \n', fg = 'red')
                change_name = input('Enter new name for existing folder: LocationReport_')
            
            report_folder = Path(Path.cwd(),'Outputs',f'LocationReport_{change_name}')    
        else:
            return "Location Report generation aborted", "yellow"
    
    # Try to make report folder
    try:
        report_folder.mkdir()
    except Exception as e:
        click.secho('Error making directory:', fg = 'red')
        click.secho(f'\t{click.format_filename(report_folder)}', fg='blue')        
        click.secho(str(e), fg = 'red')
        return "Location Report generation aborted" , "yellow"

    # Prepare for Report generation
    timerstart = time()
    click.secho('\nGenerating Location Report. Saving as HTML.', fg = 'yellow')
    
    # Read known devices
    if Path(Path.cwd(),'LocationData','Settings.json').exists():
        click.secho('\tReading named devices from "Settings.json"', fg='bright_magenta')
        with open(Path(Path.cwd(),'LocationData','Settings.json')) as reader:
            devices = json.load(reader)
            devices = pd.DataFrame.from_dict(devices['deviceSettings'])
            knownDevices = pd.DataFrame(columns = ['name','make','brand','model'])
            for i,val in enumerate(devices.deviceTag):
                device = devices.loc[i,'deviceSpec']
                knownDevices.loc[val,'name'] = devices.loc[i,'devicePrettyName']
                knownDevices.loc[val,'make'] = device['manufacturer']
                knownDevices.loc[val,'brand'] = device['brand']
                knownDevices.loc[val,'model'] = device['model']
            del devices
        del reader
        click.secho(f'\t{knownDevices.shape[0]} devices named out of {len(data.deviceTag.unique())}', fg='bright_magenta')
    else:
        knownDevices = pd.DataFrame()
 
    # Settings Read
    click.secho('\tGenerating headers and tables', fg='bright_magenta')
    read_settings, split, figure_dpi, timegaps, device_maps = config_load('location_report')

    # Begin wrting Report, Settings Summary
    report = f'<p style="font-weight:bold;font-size:20px;">Report Settings:</p>\
        <p><a href="{str(Path(Path.cwd(),"PGT.ini"))}">{str(Path(Path.cwd(),"PGT.ini"))}</a></p>\
        <div style="margin-left:5%;margin-right:50%;color:gold;background:MidnightBlue;padding:10px"> \
        <code>{read_settings}</code></div>'     
    del read_settings
    
    # Start, Stop, Obs Rate
    report = f'{report} <h1>Statistics</h1>'    
    start = data.timestamp.min().strftime('%x %X')
    end = data.timestamp.max().strftime('%x %X')
    obs_rate = round(data.shape[0]/((data.timestamp.max() - data.timestamp.min()).days*24),2)
    report = f'{report} <p style="margin-left:5%;font-weight:bold;font-size:22px;">\
               {start}<br>«»<br>{end} \
               <br><br>{obs_rate} observations per hour</p>'    
    
    # Accuracy Cutoff, Basics
    circle = np.pi*split*split*1E-6
    inside = round(100*data[data.accuracy <= split].shape[0]/data.shape[0],2)
    outside = round(100*data[data.accuracy > split].shape[0]/data.shape[0],2)
    report = f'{report}<br><h2>Accuracy Split</h2>'
    report = f'{report}<p style="margin-left:5%;font-size:20px;"> \
                {split}m radius ~ {round(circle,3)} sq km </p>\
                <p style="color:green;font-weight:bold;font-size:22px;"> \
                {inside}% of data within</p> \
                <hr style="border:5px solid green; width:{round(inside)}%; margin-left:0px;">\
                <p style="color:red;font-weight:bold;font-size:22;"> \
                {outside}% of data outside</p>\
                <hr style="border:5px solid red; width:{round(outside)}%; margin-left:0px;">\
                <br>'                
    
    # Accuracy, Timegap Table
    report = f'{report} <h2>Accuracy and Time Gap Statistics</h2>' 
    table = pd.DataFrame(data.accuracy.describe().astype('int'))\
            .join(pd.DataFrame(data.timeStep.astype("timedelta64[s]").describe().astype('int')))
    table = table.merge(pd.DataFrame(index = table.index, columns = ['']), \
                        how = 'left',  left_index = True, right_index = True) # dummy column in between the two datasets
    table = table.reindex(columns = ['accuracy', '', 'timeStep'])
    table.rename(columns = {'accuracy':'Accuracy Radius (m)', 'timeStep':'Time Gap (sec)'}, inplace = True)
    cm1 = sns.color_palette("magma", as_cmap=True)
    table = table.style.background_gradient(cmap = cm1).set_properties(**\
           {'font-weight':'bold', 'padding':'15px','text-align':'center', }).to_html().replace('nan', '')
    report = f'{report} <div style="margin-left:5%;">{table}</div>'
       
    # Notable TimeGaps
    report = f'{report} <h2>Largest Timegaps, {timegaps}</h2>'
    topGaps = data.sort_values('timeStep',ascending = False).timeStep.head(timegaps)
    table = pd.DataFrame(columns = ['Year', 'From', 'Sorter', 'To', 'Gap'])
    counter = 1
    for val in topGaps.index:
        table.loc[counter,'From'] = data.loc[val-1,'timestamp'].strftime('%x %X')[:-3]
        table.loc[counter,'Sorter'] = data.loc[val-1,'timestamp']
        table.loc[counter,'Year'] = data.loc[val-1,'timestamp'].year
        table.loc[counter,'To'] = data.loc[val,'timestamp'].strftime('%x %X')[:-3]        
        table.loc[counter,'Gap'] = topGaps[val].round('s')
        counter += 1
    del topGaps
    
    # Convert datatypes
    table['Year'] =  table['Year'].astype('int')
    table['Sorter'] =  pd.to_datetime(table['Sorter'])
    
    # Convert to Epoch for sorting
    table['Sorter'] = (table['Sorter'] - pd.Timestamp("1970-01-01", tz = 'UTC')) // pd.Timedelta("1s")
    table = table.sort_values('Sorter', ascending = False).drop(columns = 'Sorter')
    
    # Add year for grouping
    for val in table.index:
        table.loc[val,'hours'] = table.loc[val,'Gap'].total_seconds()/3600
    table.hours = table.hours.astype('int')
    
    # Reset Index, add gap rows between years
    table = table.reset_index().rename(columns = {"index":"rank"})
    for i,val in enumerate(table['Year'][:-1]):
        if val != table.loc[i+1,'Year']:
            table = pd.concat([table.loc[:i,:], pd.DataFrame(columns = \
                               table.columns, index = [-i]), table.loc[i+1:,:]])
        
    # Style and Save
    cm1 = sns.color_palette("ch:start=4,rot=-.7", as_cmap=True)
    cm2 = sns.cubehelix_palette(as_cmap=True)
    cm3 = sns.color_palette("bone_r", as_cmap=True)
    
    table = table.style.set_properties(**{'background-color': 'black', 'color': 'lightblue', 
            'font-weight':'bold', 'padding':'15px'}).hide(axis='index')\
            .background_gradient(cmap=cm1, subset = 'hours')\
            .background_gradient(cmap=cm2, subset = 'Year')\
            .text_gradient(cmap=cm3, subset='rank', high=0.5)\
            .to_html().replace("nan","")
    
    report = f'{report} <div style="margin-left:5%;">{table}</div>'
    del table, cm1, cm2, cm3
    
    # Graphing
    click.secho('\tGenerating graphs for Accuracy / Source(s) / Device(s)', fg='bright_magenta')
    report = f'{report} <h1>Graphs</h1>'
    plot_settings = {'figure.figsize':[12, 8], 'figure.facecolor':'gainsboro', 'figure.edgecolor':'k', \
      'axes.grid':True, 'grid.color':'dimgrey','axes.grid.axis':'x', 'grid.alpha':0.5, \
      'xtick.color':'k', 'xtick.labelsize': 'large', 'font.weight':'bold', 'savefig.dpi': figure_dpi}    
       
    if len(data.source.unique()) < 1:
        click.secho('No sources found in location data!', fg = 'red')
        report = f'{report} <h2>Accuracy by Source</h2> <b>No Sources found!</b>'
    else:
        # Accuracy vs Data Source, boxenplot
        counts = pd.DataFrame(data.source.value_counts())
        y_lab = []
        for val in counts.index:
            prop = round(100*counts.loc[val,'source']/data.shape[0],1)
            start = data[data.source == val].timestamp.min().strftime("%x")
            end = data[data.source == val].timestamp.max().strftime("%x") 
            y_lab.append(f'{val}\n{prop}% of data\n{start} to {end}')
        
        with plt.rc_context(plot_settings):
            sns.boxenplot(data = data, x = 'accuracy', y = 'source', order = counts.index)
            plt.xscale('log')
            
            locs, labels = plt.yticks()
            plt.yticks(ticks = locs, labels = y_lab, fontsize = 10)
            plt.ylabel('Source Type • Data % • Span', fontsize = 16, fontweight = 'bold')
            plt.xlabel('Accuracy Radius (m)', fontsize = 14, fontweight = 'bold')
            
            for ticklabel, textcolor in zip(plt.gca().get_yticklabels(), sns.color_palette()):
                ticklabel.set_color(textcolor)
                
            plt.plot([split, split], [locs.min()-0.5, locs.max()+0.5], 'k--')
            plt.text(split, locs.min()-0.55, f'{split} m', ha='center', fontweight = 'bold')
            
            savename = str(Path(report_folder,'boxer-Accuracy-Source.png'))
            plt.savefig(savename, bbox_inches = 'tight', pad_inches = 0.2, dpi = 100)
            plt.close()
           
        report = f'{report} <h2>Accuracy by Source</h2> \
        <p style="margin-left:5%;">Source(s) can be removed when filtering data. . . \
        edit <a href="{str(Path(Path.cwd(),"PGT.ini"))}">PGT.ini</a></p>   \
        <span style="margin-left:5%;color:gold;background:MidnightBlue;padding:3px"> \
        remove_sources={val} </span></p> \
        <img src="{savename}" alt="Accuracy Distribution by Source" style="width:80%;">'        
        
    if len(data.deviceTag.unique()) < 1:
        click.secho('No devices found in location data!', fg = 'red')
        report = f'{report} <h2>Accuracy by Device</h2> <b>No Devices found!</b>'
    else:    
        # Accuracy vs Device, boxenplot
        y_lab = {}
        for val in data.deviceTag.unique():
            sub = data[data.deviceTag == val].timestamp
            prop = round(100*sub.shape[0]/data.shape[0],1)
            label = f'\n{prop}% of data\n{sub.min().strftime("%x")} to {sub.max().strftime("%x")}'
            if int(val) in knownDevices.index:
                extra = f'\n{knownDevices.loc[int(val),"make"]}_{knownDevices.loc[int(val),"name"]}'               
            else:
                extra = ''
            y_lab[val] = f'{val}{extra}{label}'

        plot_settings['figure.facecolor'] = 'dimgrey'
        plot_settings['xtick.color'] = 'gainsboro'
               
        with plt.rc_context(plot_settings):
            sns.boxenplot(data = data, x = 'accuracy', y = 'deviceTag', palette = 'Set3', order = y_lab.keys())
            plt.xscale('log')
            
            locs, labels = plt.yticks()
            plt.yticks(ticks = locs, labels = y_lab.values(), fontsize = 10)
            plt.ylabel('Tag • (Name) • Data % • Span', fontsize = 16, fontweight = 'bold', color = 'white')
            plt.xlabel('Accuracy Radius (m)', fontsize = 14, fontweight = 'bold', color = 'white')
            
            for ticklabel, textcolor in zip(plt.gca().get_yticklabels(), sns.color_palette('Set3')):
                ticklabel.set_color(textcolor)
                            
            plt.plot([split, split], [locs.min()-0.5, locs.max()+0.5], 'k--')
            plt.text(split, locs.min()-0.55, f'{split} m', ha='center', fontweight = 'bold')
            
            savename = str(Path(report_folder,'boxer-Accuracy-Device.png'))
            plt.savefig(savename, bbox_inches = 'tight', pad_inches = 0.2, dpi = 100) 
            plt.close()
        
        report = f'{report} <h2>Accuracy by Device</h2> \
            <p style="margin-left:5%;">Devices(s) can be removed when filtering data. . . \
            edit <a href="{str(Path(Path.cwd(),"PGT.ini"))}">PGT.ini</a></p>   \
            <span style="margin-left:5%;color:gold;background:MidnightBlue;padding:3px"> \
            remove_devices={val} </span></p> \
            <img src="{savename}" alt="Accuracy Distribution by Device" style="width:80%;">'
        
        # Source Count for Devices        
        with plt.rc_context(plot_settings):
            ax = sns.countplot(data = data, y = 'deviceTag', hue = 'source', order = y_lab.keys(), hue_order = counts.index)
            yspan = abs(ax.get_ylim()[0]-ax.get_ylim()[1])
            yadj = 0.5*yspan/pd.DataFrame(data.groupby(['deviceTag']).source.value_counts()).shape[0]
            
            for container in ax.containers: # Bar Labels
                for val in container:
                    count = val.get_width()
                    if count > 0:
                        if count > 1E3:
                            count_label = f'{round(val.get_width()/1000,2)}k'
                        elif count > 1E6:
                            count_label = f'{round(val.get_width()/1000,2)}m'
                        else:
                            count_label = str(round(count))
                        if count / ax.get_xlim()[1] > 0.85:
                            plt.text(val.get_width()*0.5, val.xy[1]+yadj, \
                                     count_label, color = 'white', \
                                     fontsize=12, fontweight = 'bold')
                        else:                
                            plt.text(val.get_width(), val.xy[1]+yadj, count_label, \
                                     color = val.get_facecolor(), fontsize=12)
                                
            locs, labels = plt.yticks()
            plt.yticks(ticks = locs, labels = y_lab.values(), fontsize = 10)
            plt.xlabel('Count', fontsize = 14, fontweight = 'bold', color = 'white')
            plt.ylabel('Tag • (Name) • Data % • Span', fontsize = 16, fontweight = 'bold', color = 'white')
        
            for ticklabel, textcolor in zip(ax.get_yticklabels(), sns.color_palette('Set3')):
                ticklabel.set_color(textcolor)                  
    
            plt.legend(loc = 'best', frameon = False, fontsize = 14) 
            
            savename = str(Path(report_folder,'counter-Source-Device.png'))
            plt.savefig(savename, bbox_inches = 'tight', pad_inches = 0.2, dpi = 100)         
            plt.close()
            
        report = f'{report} <h2>Source Count by Device</h2> \
                <img src="{savename}" alt="Source Distribution by Device" style="width:80%;">'
        
        # Device Maps
        if device_maps:
            from .mapMe import freqmap      
            click.secho('\tGenerating device maps', fg='bright_magenta')
            report = f'{report} <h2>Device Map Links</h2> \
                    <p style="margin-left:5%; margin-right:5%;">\
                    Locations were grouped and counted after rounding (latitude,longitude) \
                    to one-hundreth of a degree. Coordinate marker size, color, and opacity \
                    were roughly scaled to their proportion, <b>"Frequency"</b> of occurence.</p> <ul>'
                     
            Path.mkdir(Path(report_folder,'maps'))
            for val in data.deviceTag.unique():
                sub = data[data['deviceTag'] == val]                
                maptitle = y_lab[val].split('\n')
                maptitle[0] = f'<b>Tag: {maptitle[0]}</b>'
                maptitle = '<br>'.join(maptitle)
                fig = freqmap(sub, maptitle)
                savename = Path(report_folder,'maps',f'{val}.html')
                fig.write_html(savename)
                report = f'{report} <li><a href="{savename}">{maptitle}</a></li><br>'
            report = f'{report} </ul>'
    
    # Write report to HTML file
    with open(Path(report_folder, 'report.html'), 'w', encoding = 'utf=8') as f:
        f.write(report)
    del f, report    
    elapsed = time() - timerstart
    click.secho('\tFinished in {:.2f} seconds \n'.format(elapsed), fg = 'green')    
    click.secho('Report generated', fg = 'yellow')
    click.secho(f'{click.format_filename(Path(report_folder, "report.html"))}\n',fg = 'blue')
    # Option to open
    click.secho('Open report in default HTML broswer? (y/n):', fg = 'cyan', nl = False)
    to_open = click.getchar()
    if to_open.lower() == 'y':
        click.launch(str(Path(report_folder, 'report.html')))
        
    return "Location reporting complete!", "green"

if __name__ == "__main__":
    pass