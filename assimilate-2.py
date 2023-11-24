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
print ('\n'*10)

#init
__appname__ = 'Assimilate.py'
__version__ = "2.00.23.11.23"

#configure argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-f", type=str, default = 'data_raw/yearly_log copy.csv',help="Input Filename - fileformat",required = False)
parser.add_argument("-c", type=str, default = './config.yaml', help="Configuration file",required = False)
parser.add_argument("-fld", type=str, default = './assimilated_data', help="Local folder for assimilated data storage",required = False)

args = parser.parse_args()
with open(args.c, 'r') as f: configuration = yaml.safe_load(f)

#define output project filenames to be saved as csv
projects_name = configuration['PROJECTS']
#define verbolsity level 
__verbosity__ = configuration['OPERATIONAL_MODE']['verbosity']

#assimilate raw data
df = raw_df = pd.read_csv(args.f)

# create a date and timestamp columns
# Group by 'project_name' and add a 'date' column
df['date'] = pd.to_datetime(df.groupby('project_name').cumcount().apply(lambda x: datetime(2022, 1, 1) + timedelta(days=x)))
df['timestamp'] = (df['date']- datetime(1970,1,1)).dt.total_seconds()

df=df[df['date'] <= datetime(2022, 12, 31)]


#slice df keeping only wanted columns
cols = [k for k in configuration['FEATURES'].keys() if configuration['FEATURES'][k]]
cols.extend(['date'])
df_s = df[cols]


#apply scalars
for feature,coef in configuration['SCALARS'].items():
    df_s[feature]=pd.to_numeric(df_s[feature], errors='coerce')*coef
    df_s[feature].replace(0,0.000001)

#create dict with df 
prjs =df_s['project_name'].unique()
dfs = {}
for prj in prjs:
    dfs[prj] = df_s.loc[df['project_name']==prj]
    # print ('\n',prj,'\n',dfs[prj].head())

#create log, cumsum, log_cumsum features    
for i,prj in enumerate(prjs):
    dfs[prj].to_csv('./assimilated_data/'+prj+'.csv')
    print ('\n',prj,'\n',dfs[prj].describe().T)

for i,prj in enumerate(prjs):
    df = pd.read_csv('./assimilated_data/'+prj+'.csv')
    for feature,coef in configuration['LOG_TRANSFORMATION'].items():
         dfs[prj].insert(0,feature+'_log',np.log(dfs[prj][feature]))
         dfs[prj].insert(0,feature+'_cumsum',dfs[prj][feature].cumsum())
         dfs[prj].insert(0,feature+'_log_cumsum',np.log(dfs[prj][feature+'_cumsum']))
    dfs[prj].to_csv('./assimilated_data/'+prj+'.csv')

#create

dfa = pd.DataFrame()
dfa.insert(0,'date',dfs[prjs[0]]['date']) 
dfa.insert(0,'timestamp',dfs[prjs[0]]['timestamp']) 

cols = [c for c in configuration['SCALARS'].keys()]

print ('---------->',cols)
for c in cols:
     arr = []
     for prj in (prjs):
         a = np.array(dfs[prj][c])
         arr.append (a)
     arr = np.array(arr)
     sarr =arr.sum(axis=0)
     dfa.insert(0,c,sarr) 
     dfa.insert(0,c+'_log',np.log(sarr))
     dfa.insert(0,c+'_cumsum',sarr.cumsum())
     dfa.insert(0,c+'_log_cumsum',np.log(sarr.cumsum()))

print(dfa.head(),'\n\n',dfa.tail())
dfa.to_csv('./assimilated_data/'+configuration['PROJECTS']['00']+'.csv')





# df.to_csv('./assimilated_data/'+configuration['PROJECTS']['00']+'.csv')
print ('\nProcess completed')