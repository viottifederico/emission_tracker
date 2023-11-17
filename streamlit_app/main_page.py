import streamlit as st
from datetime import date
import pandas as pd
import os

#debug - verbosity level for printout
versobisty = 1

st.title("ALL PROJECTS")
st.markdown("# Main page 🎈")
# st.sidebar.markdown("# Main page sidebar 🎈")
st.image("CF.jpg", use_column_width=True)

df_name = "./data_processed/whole_project/grouped_all_wildcard_df.csv"
df = pd.read_csv(df_name)
#echo to consolle - data source contents
if versobisty >1:
    print ('\n'*2,df_name,os.path.isfile(df_name))
    print (df.head(),'\n'*2,df.describe())

df_series_name = "./data_processed/whole_project/grouped_all_series_df.csv"
series = pd.read_csv(df_series_name)
#echo to consolle - data source contents
if versobisty >1:
   print ('\n'*2, df_series_name,os.path.isfile(df_series_name))
   print ('\n'*2,series.head(),'\n'*2,series.describe())


with st.container():
    col1,col2,col3,col4 = st.columns(4)
    col1.metric(label="duration", value=df["duration"].round(2), delta="55")
    col2.metric(label="emissions", value=df["emissions"].round(2), delta="1.2")
    col3.metric(label="emissions_rate", value=df["emissions_rate"].round(2), delta="-3.8")
    col4.metric(label="cpu_power", value=df["cpu_power"].round(2), delta="2.4")
    
with st.container():
    col5,col6,col7,col8 = st.columns(4)
    col5.metric(label="ram_power", value=df["ram_power"].round(2), delta="-12.5")
    col6.metric(label="cpu_energy", value=df["cpu_energy"].round(2), delta="-7.4")
    col7.metric(label="ram_energy", value=df["ram_energy"].round(2), delta="2.9")
    col8.metric(label="energy_consumed", value=df["energy_consumed"].round(2), delta="6.3")


with st.expander("show data series"):

        
    with st.container():
        st.subheader("Series Data:")
        st.data_editor(series,
                    column_config={
                        "date":st.column_config.Column(help="date", width='medium'),
                        "duration":st.column_config.NumberColumn(help="duration", width='medium'),
                        "emissions":st.column_config.NumberColumn(help="emissions", width='medium'),
                        "emissions_rate":st.column_config.NumberColumn(help="emissions_rate", width='medium'),
                        "cpu_power":st.column_config.NumberColumn(help="cpu_power", width='medium'),
                        "ram_power":st.column_config.NumberColumn(help="ram_power", width='medium'),
                        "cpu_energy":st.column_config.NumberColumn(help="cpu_energy", width='medium'),
                        "ram_energy":st.column_config.NumberColumn(help="ram_energy", width='medium'),
                        "energy_consumed":st.column_config.NumberColumn(help="energy_consumed", width='medium')
                    }, 
                    hide_index=True, 
                    use_container_width=True
                    )
        
    
st.line_chart(series['duration'])
st.scatter_chart(series, x='duration', y='emissions')



