import streamlit as st
from datetime import date
import pandas as pd
import numpy as np
import os,pprint
import matplotlib.pyplot as plt
import plotly.figure_factory as ff

#purpose : returns  value from "Total" dataframe row.
#  input : d , df row converted to dict
#          k , keyword (df column)
#          roundup_digits, optional, default is 2
#
def from_dict_get_value(dictionary = None, keyword = None, roundup_digits = 2):
    return round(list(dictionary[keyword].values())[0],roundup_digits)

#purpose : retunrs np array given projectName, ColumnNane, optionally start and stop can be given
#  input : projectName,str  must match with existing file in hardcoded data folder
#          ColumnNane, str must be an existing column in the provided dataset
#          datetime_start, str format "2022-11-24" it is the first record collated into the output array, it must be in the past respect to datetime_end
#          datetime_end, str format "2022-12-04" it is the last record collated into the output array, it must be in the future respect to datetime_start

def from_projectName_get_values(projectName = None, ColumnNme = None, datetime_start = None, datetime_end = None):
    df = pd.read_csv('assimilated_data/'+projectName+'.csv')
    n_rows =  len(df. index)
    if ColumnNme in df.columns.values : 
        if datetime_start is not None: 
            i_idx = np.where(df['date'] == datetime_start)[0][0]
        else : i_idx = 0
        if datetime_end is not None: 
            e_idx = np.where(df['date'] == datetime_end)[0][0]
        else : e_idx = n_rows
    arr = np.array(df[ColumnNme].iloc[list(range(i_idx,e_idx))])
    return {'array':arr,'feature':ColumnNme, 'projectName':projectName,'datetime_serie':np.array(df['date'].iloc[list(range(i_idx,e_idx))])}



#debug - verbosity level for printout
versobisty = 1

# st.title("ALL PROJECTS")
# st.markdown("# Main page 🎈")
# st.sidebar.markdown("# Main page sidebar 🎈")
st.image("./resources/CF.png", use_column_width=True)
st.markdown(r"""
# 12 MONTHS ROLLING TOTALS 
""")


df_name = "./assimilated_data/Totals.csv"
df = pd.read_csv(df_name)
#gets the totals which are written always in the last row
totals = df.tail(1).to_dict() 

with st.container():
    col1,col2,col3,col4 = st.columns(4)
    col1.metric(label="duration", value=from_dict_get_value(dictionary= totals, keyword = 'duration'), delta="55")
    col2.metric(label="emissions", value=from_dict_get_value(dictionary= totals, keyword = 'emissions'), delta="1.2")
    col3.metric(label="emissions_rate", value=from_dict_get_value(dictionary= totals, keyword = 'emissions_rate'), delta="-3.8")
    col4.metric(label="cpu_power", value=from_dict_get_value(dictionary= totals, keyword = 'cpu_power'), delta="2.4")

with st.container():
    col5,col6,col7,col8 = st.columns(4)
    col5.metric(label="ram_power", value=from_dict_get_value(dictionary= totals, keyword = 'ram_power'), delta="55")
    col6.metric(label="cpu_energy", value=from_dict_get_value(dictionary= totals, keyword = 'cpu_energy'), delta="1.2")
    col7.metric(label="ram_energy", value=from_dict_get_value(dictionary= totals, keyword = 'ram_energy'), delta="-3.8")
    col8.metric(label="energy_consumed", value=from_dict_get_value(dictionary= totals, keyword = 'energy_consumed'), delta="2.4")

columns_names = df.columns.values[2::]
with st.container():
     selected_feature = st.selectbox('Please, select the feature you want to show',columns_names)


project_names = df['project_name'].tolist()[0:-1]
labels = project_names
sizes = df[selected_feature].to_list()[0:-1]
explode = (0, 0.1, 0)  

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',shadow=True, startangle=90)
ax1.axis('equal')  
ax1.set_title(selected_feature.upper())


# Create two columns
cols = st.columns(1)

cols[0].pyplot(fig1)
# cols[1].pyplot(fig2)

# st.pyplot(fig1)


Opt_SemiLogYChart = st.checkbox('Log chart')

# Collate data for line chart
#given feature is runtime collated into a dataframe for all projects
t_df=pd.DataFrame()                               #empty df
for i in range(len(project_names)):               #loop on project names 
  entry = from_projectName_get_values(project_names[i], selected_feature,datetime_start='2022-01-25',datetime_end='2022-11-25')  #extract data
  arr = entry['array']+0.000000000001 # offset to prevent exception with log transformation
  if Opt_SemiLogYChart: arr =  np.log(arr)    #on demand transform to log 
  t_df[entry['projectName']]=arr              #add column to df
t_df['date']=entry['datetime_serie']          #add independent axis (date) 

#render the line chart
st.line_chart(t_df, x= 'date', y=project_names,color =['#1f77b4','#ff7f0e','#2ca02c'])

arr = []
for prj in project_names:               #loop on project names 
   arr.append(t_df[prj])
print (arr)
fig = ff.create_distplot(arr, project_names)
st.plotly_chart(fig, use_container_width=True)

quit()















