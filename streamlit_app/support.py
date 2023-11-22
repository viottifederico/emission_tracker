import datetime,calendar, yaml 
import numpy as np
from base64 import b64encode

# '''
# Status management
# '''
# class Status():
#     def __init__(self):
#         self.status_filename = 'status.yml'
#         self.current = None
#         self.get_status()
    
#     #rertrieve status
#     def get_status(self):
#         with open(self.status_filename , 'r') as fobj: 
#             self.current = yaml.safe_load(fobj)    
#         return self.current    

#     #store status
#     def push_status(self):
#         with open(self.status_filename, 'w') as fobj:
#              self.current = yaml.dump(self.current, fobj)    

#     #store status
#     def update(self, kw=None, value =None, quiet = False):
#         self.get_status()
#         if kw in self.current['STATUS']:
#             if value is None : value = 'None'
#             self.current['STATUS'][kw]=value
#         self.push_status()
#         if quiet == False:
#            print('Class STATUS : update performed on kw ',kw, 'with value ', value,' \n',self.get_status())  

#     #reset status
#     def reset(self):        
#         for kw in self.current['STATUS']:
#             self.update(kw=kw,value=None, quiet = True)
#         print('Class STATUS : reset performed\n',self.get_status())    


'''
 Image tools
'''
# purpose : read image and returns its bytes repr (required to insert an image in streamlit markdown html)
# input : image file
#output : byte reprsentation
# 
def img_to_bytes(img_path):
    with open(img_path, 'rb') as f:
         img_bytes = f.read()
    encoded = b64encode(img_bytes).decode()
    return encoded

'''
Dataframe operations
'''

#purpose : get the row index provided timestamp (epoch). 
#imput : 
#        daily_df_dict : dict,  which contains dataframes of each project, key is project name
#        timestamp (ux epoch)
#output: index (cardinal)
#
def from_timestamp_get_row(daily_df_dict,ts):
    df =daily_df_dict[list(daily_df_dict.keys())[0]]
    return np.where(df.timestamp >= ts)[0][0]

#purpose : returns  value from "Total" dataframe row.
#  input : d , df row converted to dict
#          k , keyword (df column)
#          roundup_digits, optional, default is 2
# output
#         float
def from_dict_get_value(dictionary = None, keyword = None, roundup_digits = 2):
    return round(list(dictionary[keyword].values())[0],roundup_digits)

#purpose : from daily data dict get wanted column of wanted proj
# input : 
#         daily_df_dict : dict (container of dataframes)
#         projectName : str
#         columName : str
# output :
#         np array
#
def from_df_get_values(daily_df_dict = None, projectName = None,columnName = None):
    arr = np.array(daily_df_dict[projectName][columnName])
    datetime_arr = np.array(daily_df_dict[projectName]['date'])
    return arr,datetime_arr

# purpose slice all daily df accordingly to left and right indexes
# input : 
#        daily df dictionary : dict,  which contains dataframes of each project, key is project name
#        left_index : int,  inital cutting point
#        right_index : int,  final cutting point
# output: 
#        daily df dictionary where each df is sliced
def slice_df(daily_df_dict, left_index,right_index):
    indices = list(range(left_index,right_index-1))
    sliced_df={}
    projecNames = list(daily_df_dict.keys())
    for proj in projecNames:
        sliced_df[proj]= daily_df_dict[proj].iloc[indices]
    return sliced_df    
