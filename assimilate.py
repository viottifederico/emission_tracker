"""
ASSIMILATE.py

Description : utility to preprocess raw data whose aim is to create input data to be used by streamlit objects
"""
import argparse
import pandas as pd
import yaml
import functools as ft
import numpy as np
from datetime import datetime, timedelta

#init
__appname__ = 'Assimilate.py'
__version__ = "1.10.21.11.23"

#configure argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-f", type=str, default = 'data_raw/yearly_log copy.csv',help="Input Filename - fileformat",required = False)
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

#show raw data source (local csv file)
if __verbosity__ >= 1 : print('\t{0:>30s} : {1:<50s}'.format('Source filename', args.f))

#Source data assimilation, with columns preservation (hardcoded)
raw_df = pd.read_csv(args.f)
# Apply columns selection
raw_df = raw_df[colums_to_preserve]
# Apply scalars
if Apply_scalars:
    for c in configuration['SCALARS'].keys(): 
        raw_df[c] = raw_df[c] * configuration['SCALARS'][c]        
        raw_df[c+'_cumsum'] = raw_df[c].cumsum()
        if Log_transformation:
            if c in list(configuration['LOG_TRANSFORMATION'].keys()):
                raw_df[c+'_log']=np.log(raw_df[c].replace(0,0.000000000001))
                raw_df[c+'_cumsum_log']=np.log(raw_df[c+'_cumsum'].replace(0,0.000000000001))
print (raw_df.columns)        
# Compute cumulated series        
if __verbosity__ >= 1 : print('\t{0:>30s} : {1:<6d}'.format('columns', len(colums_to_preserve)))
if __verbosity__ >= 1 : print('\t{0:>30s} : {1:<6d}'.format('rows', len(raw_df.index)))

# create a datetime colum so to have a single daily entry for each project 
# Group by 'project_name' and add a 'date' column
raw_df['date'] = pd.to_datetime(raw_df.groupby('project_name').cumcount().apply(lambda x: datetime(2022, 1, 1) + timedelta(days=x)))
#convert the newly created data to unix epoch so to have a linear time axis
raw_df['timestamp2'] = (raw_df['date']- datetime(1970,1,1)).dt.total_seconds()


dfs =[]
if __verbosity__ >= 1: print('\n\t{0:>30s} | {1:<16s} \n\t{2:>30s} | {3:<16s} '.format('Project name','duration [days]','-'*30,'-'*16))
for project_name in raw_df['project_name'].unique():
    dfs.append(raw_df[raw_df['project_name']==project_name][:]) 
    raw_df[raw_df['project_name']==project_name][:].to_csv(args.fld+'/'+project_name+'.csv')
    if __verbosity__ >= 1: print('\t{0:>30s} | {1:<16d}'.format(project_name,len(raw_df[raw_df['project_name']==project_name])))

dfs = []
for project_name in raw_df['project_name'].unique():
    dfs.append(raw_df[raw_df['project_name']==project_name][:])

# cols = ['duration','emissions','emissions_rate','cpu_energy','ram_energy','energy_consumed']
cols =[af for af in list(configuration['FEATURES'].keys()) if configuration['FEATURES'][af]==True][2::]

temp_list = [n+'_cumsum' for n in cols]
cols.extend(temp_list)
merged_df = pd.DataFrame()
merged_df.insert(0,'timestamp',np.array(dfs[0]['timestamp']),True)

print ('---->',cols, len(dfs))
for i_d in dfs:
    print (len(i_d(i_d['date'] < da)))    
# if Apply_scalars:
#     for c in configuration['SCALARS'].keys(): 
#         raw_df[c] = raw_df[c] * configuration['SCALARS'][c]        
#         raw_df[c+'_cumsum'] = raw_df[c].cumsum()
#         if Log_transformation:
#             if c in list(configuration['LOG_TRANSFORMATION'].keys()):
#                 raw_df[c+'_log']=np.log(raw_df[c].replace(0,0.000000000001))
#                 raw_df[c+'_cumsum_log']=np.log(raw_df[c+'_cumsum'].replace(0,0.000000000001))


merged_df = pd.concat(dfs).groupby(["date"], as_index=False)[cols].sum()


for c in cols:
    arr = np.log(merged_df[c].replace(0,0.000000000000001))
    merged_df.insert(0,c+'_log',arr,True)


#build serie with label 
arr = ['Cumulated' for i in range(len(merged_df)) ]
merged_df.insert(0,'project_name',arr,True)
merged_df.insert(0,'timestamp',np.array(dfs[0]['timestamp']),True)
merged_df.to_csv(args.fld+'/All_projects.csv')


#completion warning
if __verbosity__ >= 1: print ('\n Process completed.')