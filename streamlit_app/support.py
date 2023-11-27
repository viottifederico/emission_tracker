import datetime,calendar, yaml 
import numpy as np
from base64 import b64encode


import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer 
import pandas as pd

def build_subpage(streamlit_obj, title,df_csv):
    streamlit_obj.set_page_config(layout="wide")
    streamlit_obj.title(title)
    df = pd.read_csv(df_csv)
    df = df.drop(columns= ['project_name','timestamp','Unnamed: 0'])
    _cols = list(df.columns    )
    _cols.remove('date')
    with streamlit_obj.expander("Series Data:"):
         filtered_df = dataframe_explorer(df, case=False)
         streamlit_obj.dataframe(filtered_df, use_container_width=True)
    x_ax = streamlit_obj.selectbox('Select the x label',_cols, index=12)
    y_ax = streamlit_obj.selectbox('Select the y label',_cols, index=8)
    import plotly.express as px
    fig = px.scatter(filtered_df, x=x_ax, y=y_ax,  marginal_y="box",
                marginal_x="box", trendline="ols", template="simple_white")
    streamlit_obj.plotly_chart(fig,  use_container_width=True)
    


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
