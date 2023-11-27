import streamlit as st
import datetime,calendar ,yaml
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
#custom functions 
from support import *

#print ('\n'*100)
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
    #list all files is assiilated repository 

    #assimilate daily data
    _daily_data_df={}
    for proj in  _configuration['PROJECTS'].values(): 
        _daily_data_df[proj] = pd.read_csv('assimilated_data/'+proj+'.csv')
    return {'cnf':_configuration,'daily_data':_daily_data_df,'entries':len(_daily_data_df[proj])}
  

#-----------------------------------------------------------------------------------------------------------
#build main page  
st.set_page_config(layout="wide")

#load data
d = load_data()
#active_features from config file
active_features =[af for af in list(d['cnf']['FEATURES'].keys()) if d['cnf']['FEATURES'][af]==True][2::]
print ('\nactive_features\n',active_features)


#retireve whole period initial and final date
i_dte = list(map(int,d['daily_data'][list(d['daily_data'].keys())[0]]['date'].iloc[0].split('-')))
e_dte = list(map(int,d['daily_data'][list(d['daily_data'].keys())[0]]['date'].iloc[-1].split('-')))
#assemple daetime obj required by the double ended slider
i_dt_obj=datetime.date(i_dte[0],i_dte[1],i_dte[2])
e_dt_obj=datetime.date(e_dte[0],e_dte[1],e_dte[2])

#define logo
logo_img_filename = "./resources/rsz_1cf-mod_wip.png"
log_img = "<img src='data:image/png;base64,{}' class='img-fluid' tooltip='ET Logo'>".format(img_to_bytes(logo_img_filename))
md_html_string = "<p style='text-align: center; color: grey;'>"+log_img+"</p>" #to be published using st.markdown


#computes required resources for WHOLE PERIOD zero carbon emission balance
prj = d['cnf']['PROJECTS']['00']
print(prj)
cumulated_emmissions = d['daily_data'][prj]['emissions_cumsum'].iloc[-1]
trees_to_plant_min  = "{0:3.0f}".format(cumulated_emmissions/d['cnf']['CARBON_BALANCE']['tree_co2kg_ratio_min'])
trees_to_plant_max  = "{0:3.0f}".format(cumulated_emmissions/d['cnf']['CARBON_BALANCE']['tree_co2kg_ratio_max'])
area_needed = "{0:3.0f}".format(10000*(cumulated_emmissions/d['cnf']['CARBON_BALANCE']['tree_co2kg_ratio_min']) / d['cnf']['CARBON_BALANCE']['trees_per_hectare_avg'])


# define icons for Yearly Balance
#encode images to be inserted in markdown 
img_tree = "<img src='data:image/png;base64,{}' class='img-fluid' tooltip='required land to plant the trees'>".format(img_to_bytes("resources/trees.png"))
img_land = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(img_to_bytes("resources/parcel.png"))
#build html string to be inserted in the markdown
summary_tables = '<style>h1 {text-align:center;} h2 {text-align:center;}</style><h1>ZERO EMISSION BALANCE</h1><h2>Y E A R L Y</h2><table width="100%">	<col style="width:30%">	<col style="width:70%">	<tbody>	<tr><td>'+img_land+'</td><td><h2>'+area_needed+' m<sup style="font-size:.8em;">2</sup></h2></td></tr><tr><td>'+img_tree+'</td><td><h2>'+trees_to_plant_max+' - '+trees_to_plant_min+'</h2></td>	</tr></tbody></table>'

#build page layout
#crerate containers
col1, col2 = st.columns([2, 1])
#render logo column
with col1:
    st.markdown( md_html_string, unsafe_allow_html=True)
#render summary colum 
with col2:
    st.markdown(summary_tables,unsafe_allow_html=True)

#build interactive section
#create containers
with st.container():
    col1, col2 = st.columns([1, 4])
#add selection boxes and log option checkbox
projectsName = list(d['daily_data'].keys())
with col1: 
    log_opt = st.checkbox('Use Logarithmic scale')
    cumsum_opt = st.checkbox('Cumulated distribution')
#add double ended slider
with col2:
    slider = st.slider(':green[Select date range]', min_value=i_dt_obj, value=(i_dt_obj, e_dt_obj), max_value=e_dt_obj,  key='DateSlider')



with st.container():
    col1, col2 = st.columns([1, 4])
with col1: 
    selected_projects = st.multiselect('Select the projects to show',projectsName,default=projectsName[-1],key='SelectedProjects_ms')
    selected_feature = st.selectbox('Select the feature to show',active_features, key='SelectedFeature_sb')
    selected_chart = st.selectbox('Select chart type',['Daily Line chart :shark:', 'Daily Distribution plot'], key='SelectedChart_sb')

if len(selected_projects) > 0:
     res = st.session_state.DateSlider
     left_ts = calendar.timegm(res[0].timetuple())
     right_ts = calendar.timegm(res[1].timetuple())
     left_idx = from_timestamp_get_row(d['daily_data'],left_ts)
     right_idx = from_timestamp_get_row(d['daily_data'],right_ts)
     s_df = slice_df(d['daily_data'],left_idx,right_idx)
     projectNames = list(d['daily_data'].keys())
     t_df = pd.DataFrame()
     selected_feature = st.session_state.SelectedFeature_sb
     if cumsum_opt : 
        selected_feature=selected_feature+'_cumsum'
     elif log_opt :
         selected_feature=selected_feature+'_log'
     elif log_opt :
         selected_feature=selected_feature+'_log_cumsum'
    #
    #build temp dataframe for charting 
     for proj in selected_projects:
         arr, date_arr = from_df_get_values(s_df,proj,selected_feature)
         if '_cumsum' in selected_feature:
             arr = arr-arr[0]
         t_df[proj]=arr
     t_df['date']=date_arr

     out = s_df['All_projects'][['duration','emissions','emissions_rate','energy_consumed']].sum().to_dict()
     out['emissions_rate'] = out['emissions_rate']/len(s_df['All_projects']['emissions_rate']) 
     whole = d['daily_data']['All_projects'][['duration','emissions','emissions_rate','energy_consumed']].sum().to_dict()
     whole['emissions_rate'] = whole['emissions_rate']/d['entries']
     with col2:
     
         print (type(out), out, whole)
     #render metrics
         with st.container():
        #    col1,col2,col3,col4 = st.columns(4)
        #    v = "{0:.3f}".format(100*round(out['duration']/whole['duration'],3))+' %'
        #    col1.metric(label="Total duration".upper(), value=round(out['duration'],2), delta=v)
        #    v = str(100*round(out['emissions']/whole['emissions'],2))+' %'
        #    col2.metric(label="Total emissions".upper(), value=round(out['emissions'],2), delta=v)
        #    v = str(100*round(out['emissions_rate']/whole['emissions_rate'],2))+' %'
        #    col3.metric(label="Average emissions rate".upper(), value=round(out['emissions_rate'],2), delta=v)
        #    v = str(100*round(out['energy_consumed']/whole['energy_consumed'],2))+' %'
        #    col4.metric(label="Total energyconsumed".upper(), value=round(out['energy_consumed'],2), delta=v)
           col1,col2,col3 = st.columns(3)
           v = str(100*round(out['emissions']/whole['emissions'],2))+' %'
           col1.metric(label="Total emissions".upper(), value=round(out['emissions'],2), delta=v)
           v = str(100*round(out['emissions_rate']/whole['emissions_rate'],2))+' %'
           col2.metric(label="Average emissions rate".upper(), value=round(out['emissions_rate'],2), delta=v)
           v = str(100*round(out['energy_consumed']/whole['energy_consumed'],2))+' %'
           col3.metric(label="Total energyconsumed".upper(), value=round(out['energy_consumed'],2), delta=v)
         #add chart 
         if selected_chart in ['Daily Line chart']:
             lnc =  st.line_chart(t_df, x="date", y=selected_projects)
        #  elif selected_chart in ['Daily Line chart']:
        #      lnc = st.line_chart(t_df, x="date", y=selected_projects)
         elif selected_chart in ['Daily Distribution plot']:
             hist_data =[]
             projects = []
             for proj in t_df.columns: 
               if proj != 'date': projects.append(proj)
             for prj in  projects:
                 hist_data.append(np.array(t_df[prj]))
             fig = ff.create_distplot(hist_data, projects)    
             fig.update_layout(legend=dict( yanchor="bottom",y=-0.5,xanchor="right"))
             fig.update_layout(title_text='Distribution Plot: ' + selected_feature )
             st.plotly_chart(fig,  use_container_width=True)
     #add metrics for the selected period
     #compute values


