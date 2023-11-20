"""
ASSIMILATE.py

Description : utility to preprocess raw data whose aim is to create input data to be used by streamlit objects
"""
import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

#init
__appname__ = 'Assimilate.py'
__version__ = "1.00.17.11.23"
__verbosity__ = 1
if __verbosity__ >= 1 : print('\n'*10+'\t{0:>30s} : {1:<50s}\n'.format(__appname__, __version__))

#configure argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-f", type=str, help="Input Filename - fileformat",required = False)
parser.add_argument("-fld", type=str, default = './assimilated_data', help="Local folder for assimilated data storage",required = False)

args = parser.parse_args()

#define raw data source (local csv file)
if args.f is None: 
    args.f = "data_raw/yearly_log copy.csv"
if __verbosity__ >= 1 : print('\t{0:>30s} : {1:<50s}'.format('Source filename', args.f))

#Source data assimilation, with columns preservation (hardcoded)
raw_df = pd.read_csv(args.f)
colums_to_preserve = ['timestamp','project_name','duration','emissions','emissions_rate','cpu_energy','cpu_power','ram_power','ram_energy','energy_consumed',
                      'longitude','latitude']
raw_df = raw_df[colums_to_preserve]
if __verbosity__ >= 1 : print('\t{0:>30s} : {1:<6d}'.format('columns', len(colums_to_preserve)))
if __verbosity__ >= 1 : print('\t{0:>30s} : {1:<6d}'.format('rows', len(raw_df.index)))

# Value harmoziation for rendering
raw_df['duration'] = raw_df['duration'] * 100
raw_df['emissions'] = raw_df['emissions'] * 100000000
raw_df['emissions_rate'] = raw_df['emissions_rate'] * 100000000
raw_df['cpu_energy'] = raw_df['cpu_energy'] * 1000000
raw_df['ram_energy'] = raw_df['ram_energy'] * 1000000
raw_df['energy_consumed'] = raw_df['energy_consumed'] * 1000000

# create a datetime colum so to have a single daily entry for each project 
# Group by 'project_name' and add a 'date' column
raw_df['date'] = pd.to_datetime(raw_df.groupby('project_name').cumcount().apply(lambda x: datetime(2022, 1, 1) + timedelta(days=x)))
raw_df.pop('timestamp')

#compute sum of all numeric columns and store in a new df
Totals_df= raw_df.groupby('project_name').agg({'duration': 'sum','emissions': 'sum','emissions_rate': 'sum','cpu_power': 'sum',
                                             'ram_power': 'sum','cpu_energy': 'sum','ram_energy': 'sum','energy_consumed': 'sum'}).reset_index()

Totals_df.loc[len(Totals_df)] =  ['All_Projects']+Totals_df.sum(numeric_only=True, axis=0).tolist()
if __verbosity__ >= 1 : print ('\nTotals  for all data grouped by project\n','-'*34,'\n',Totals_df)

#create CSVs
Totals_df.to_csv(args.fld+'/Totals.csv')
if __verbosity__ >= 1: print('\n\t{0:>30s} | {1:<16s} \n\t{2:>30s} | {3:<16s} '.format('Project name','duration [days]','-'*30,'-'*16))
for project_name in raw_df['project_name'].unique():
    raw_df[raw_df['project_name']==project_name][:].to_csv(args.fld+'/'+project_name+'.csv')
    if __verbosity__ >= 1: print('\t{0:>30s} | {1:<16d}'.format(project_name,len(raw_df[raw_df['project_name']==project_name])))

#completion warning
if __verbosity__ >= 1: print ('\n Process completed.')