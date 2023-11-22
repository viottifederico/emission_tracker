import streamlit as st
import datetime,calendar 
import pandas as pd
import numpy as np
import os, pprint, yaml
import plotly.express as px
import plotly.figure_factory as ff

from support import *



print ('\n'*100)

# Purpse cache configuration and dataframes
# no input required
# returns : dict
#     cnf : dict (configuration)
#     totals :  pandas df
#     daily_data: _dict (of pandas df, key is project name)
#
# WARNING : HARDCODED CONST (file names)
#
# @st.cache_data
def load_data():
    #assimilate configuration dict
    configuration_filename = 'config.yaml'
    with open(configuration_filename , 'r') as f: _configuration = yaml.safe_load(f)
    #assimilate Totals
    df_name = "./assimilated_data/Totals.csv"
    _totals_df = pd.read_csv(df_name)
    #assimilate daily data
    _daily_data_df={}
    for proj in  _totals_df['project_name'].tolist()[0:-1]: _daily_data_df[proj] = pd.read_csv('assimilated_data/'+proj+'.csv')
    _daily_data_df['Cumulated'] = pd.read_csv('assimilated_data/All_projects.csv')
    return {'cnf':_configuration,'totals':_totals_df,'daily_data':_daily_data_df}
  

#-----------------------------------------------------------------------------------------------------------
#build main page  
st.set_page_config(layout="wide")
col1, col2 = st.columns([3, 1])
col1.image("./resources/CF.png", use_column_width=True)

#load data
d = load_data()
#active_features from config file
active_features =[af for af in list(d['cnf']['FEATURES'].keys()) if d['cnf']['FEATURES'][af]==True][2::]


#retireve whole period initial and final date
i_dte = list(map(int,d['daily_data'][list(d['daily_data'].keys())[0]]['date'].iloc[0].split('-')))
e_dte = list(map(int,d['daily_data'][list(d['daily_data'].keys())[0]]['date'].iloc[-1].split('-')))
#assemple daetime obj required by the double ended slider
i_dt_obj=datetime.date(i_dte[0],i_dte[1],i_dte[2])
e_dt_obj=datetime.date(e_dte[0],e_dte[1],e_dte[2])

#computes required resources for whole period zero carbon emission balance
trees_to_plant_min  = "{0:3.0f}".format(d['totals']['emissions'].to_list()[-1]/d['cnf']['CARBON_BALANCE']['tree_co2kg_ratio_min'])
trees_to_plant_max  = "{0:3.0f}".format(d['totals']['emissions'].to_list()[-1]/d['cnf']['CARBON_BALANCE']['tree_co2kg_ratio_max'])
area_needed = "{0:3.0f}".format(10000*(d['totals']['emissions'].to_list()[-1]/d['cnf']['CARBON_BALANCE']['tree_co2kg_ratio_min']) / d['cnf']['CARBON_BALANCE']['trees_per_hectare_avg'])

# build page elements
#encode images to be inserted in markdown 
img_tree = "<img src='data:image/png;base64,{}' class='img-fluid' tooltip='required land to plant the trees'>".format(img_to_bytes("resources/trees.png"))
img_land = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(img_to_bytes("resources/parcel.png"))
#build html string to be inserted in the markdown
s = '<style>h1 {text-align:center;} h2 {text-align:center;}</style><h1>ZERO EMISSION BALANCE</h1><h2>Y E A R L Y</h2><table width="100%">	<col style="width:30%">	<col style="width:70%">	<tbody>	<tr><td>'+img_land+'</td><td><h2>'+area_needed+' m<sup style="font-size:.8em;">2</sup></h2></td></tr><tr><td>'+img_tree+'</td><td><h2>'+trees_to_plant_max+' - '+trees_to_plant_min+'</h2></td>	</tr></tbody></table>'

#render the page elements
#resources needed to 0 balance
col2.header('',divider='rainbow')
with col2:
    st.markdown(s,unsafe_allow_html=True)
col2.header('',divider='rainbow')
#add metrics
with st.container():
    col1,col2,col3,col4 = st.columns(4)
    col1.metric(label="duration".upper(), value=round(d['totals']['duration'].to_list()[-1],2), delta="n.d.")
    col2.metric(label="emissions".upper(), value=round(d['totals']['emissions'].to_list()[-1],2), delta="n.d.")
    col3.metric(label="emissions_rate".upper(), value=round(d['totals']['emissions_rate'].to_list()[-1],2), delta="n.d.")
    col4.metric(label="energy_consumed".upper(), value=round(d['totals']['energy_consumed'].to_list()[-1],2), delta="n.d.")

with st.container():
    col1, col2 = st.columns([1, 4])
#add double ended slider
projectsName = list(d['daily_data'].keys())
with col1: 
    log_opt = st.checkbox('Use Logarithmic scale')
    selected_projects = st.multiselect('Select the projects to show',projectsName,default=projectsName[-1],key='SelectedProjects_ms')
    selected_feature = st.selectbox('Select the feature to show',active_features, key='SelectedFeature_sb')
    selected_chart = st.selectbox('Select chart type',['Line chart', 'Distribution plot'], key='SelectedChart_sb')
with col2:
    slider = st.slider(':green[Select date range]', min_value=i_dt_obj, value=(i_dt_obj, e_dt_obj), max_value=e_dt_obj,  key='DateSlider')

if len(selected_projects) == 0:
    selected_projects = projectsName[-1]
else: 
 res = st.session_state.DateSlider
 left_ts = calendar.timegm(res[0].timetuple())
 right_ts = calendar.timegm(res[1].timetuple())
 left_idx = from_timestamp_get_row(d['daily_data'],left_ts)
 right_idx = from_timestamp_get_row(d['daily_data'],right_ts)
 s_df = slice_df(d['daily_data'],left_idx,right_idx)
 projectNames = list(d['daily_data'].keys())
 t_df = pd.DataFrame()
 selected_feature = st.session_state.SelectedFeature_sb
 if log_opt :
     selected_feature=selected_feature+'_log'
#build temp dataframe for charting 
 for proj in selected_projects:
     arr, date_arr = from_df_get_values(s_df,proj,selected_feature)
     t_df[proj]=arr
 t_df['date']=date_arr


#  with st.container():
#      col1, col2 = st.columns([1, 4])

 with col2:
        if selected_chart in ['Line chart']:
            st.line_chart(t_df, x="date", y=selected_projects)
        elif selected_chart in ['Distribution plot']:
            hist_data =[]
            projects = []
            for proj in t_df.columns: 
              if proj != 'date': projects.append(proj)
            for prj in  projects:
                hist_data.append(np.array(t_df[prj]))
            fig = ff.create_distplot(hist_data, projects)    
            fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
))
            st.plotly_chart(fig, use_container_width=True)




