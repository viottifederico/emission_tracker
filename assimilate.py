"""
ASSIMILATE.py

Description : utility to preprocess raw data whose aim is to create input data to be used by streamlit objects
"""
import argparse
import pandas as pd
import yaml
import numpy as np
from datetime import datetime, timedelta

#init
__appname__ = 'Assimilate.py'
__version__ = "1.10.21.11.23"

#configure argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-f", type=str, help="Input Filename - fileformat",required = False)
parser.add_argument("-c", type=str, default = './config.yaml', help="Configuration file",required = False)
parser.add_argument("-fld", type=str, default = './assimilated_data', help="Local folder for assimilated data storage",required = False)

args = parser.parse_args()
with open(args.c, 'r') as f: configuration = yaml.safe_load(f)

#define verbolsity level 
__verbosity__ = configuration['OPERATIONAL_MODE']['verbosity']
#define Log_transformation
Log_transformation =configuration['OPERATIONAL_MODE']['log_transformation']
Apply_scalars = configuration['OPERATIONAL_MODE']['apply_scalars']

#define columns to preserve
colums_to_preserve = [k for k in configuration['FEATURES'].keys() if configuration['FEATURES'][k]]

if __verbosity__ >= 1 : print('\n'*10+'\t{0:>30s} : {1:<50s}\n'.format(__appname__, __version__))

#define raw data source (local csv file)
if args.f is None: args.f = "data_raw/yearly_log copy.csv"
if __verbosity__ >= 1 : print('\t{0:>30s} : {1:<50s}'.format('Source filename', args.f))

#Source data assimilation, with columns preservation (hardcoded)
raw_df = pd.read_csv(args.f)
# Apply columns selection
raw_df = raw_df[colums_to_preserve]
# Apply scalars
if Apply_scalars:
    for c in configuration['SCALARS'].keys():
        raw_df[c] = raw_df[c] * configuration['SCALARS'][c]        
# Apply Log transformation
if Log_transformation:
    for c in configuration['LOG_TRANSOFRMATION'].keys():
        if configuration['LOG_TRANSOFRMATION'][c]: raw_df[c+'_log']=np.log(raw_df[c])

if __verbosity__ >= 1 : print('\t{0:>30s} : {1:<6d}'.format('columns', len(colums_to_preserve)))
if __verbosity__ >= 1 : print('\t{0:>30s} : {1:<6d}'.format('rows', len(raw_df.index)))

# create a datetime colum so to have a single daily entry for each project 
# Group by 'project_name' and add a 'date' column
raw_df['date'] = pd.to_datetime(raw_df.groupby('project_name').cumcount().apply(lambda x: datetime(2022, 1, 1) + timedelta(days=x)))
raw_df.pop('timestamp')

# Rules for Aggregation
rfa = {k:'sum' for k in configuration['SCALARS'].keys()}
rfa.update({k+'_log':'sum' for k in configuration['SCALARS'].keys()})

# Totals by project
Totals_df= raw_df.groupby('project_name').agg(rfa).reset_index()
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