import yaml, datetime
import pandas as pd
import numpy as np
#streamlit
import streamlit as st
from st_clickable_images import clickable_images
from streamlit_extras.switch_page_button import switch_page


#charting
import plotly.figure_factory as ff
import plotly.express as px
#custom functions 
from support import *

__version__ = 3.0

#-----------------------------------------------------------------------------------------------------------
# @st.cache_data
#-----------------------------------------------------------------------------------------------------------
def load_data():
    '''
    Purpse cache configuration and dataframes
       no input required
       returns : dict
           cnf : dict (configuration)
           daily_data: _dict (of pandas df, key is project name)
           entries : number of rows in daily_data
       WARNING : HARDCODED CONST (file names)
    '''
    #assimilate configuration dict
    configuration_filename = 'config.yaml'
    with open(configuration_filename , 'r') as f: _configuration = yaml.safe_load(f)
    #list all files is assiilated repository 

    #assimilate daily data
    _daily_data_df={}
    for proj in  _configuration['PROJECTS'].values(): 
        _daily_data_df[proj] = pd.read_csv('assimilated_data/'+proj+'.csv')
        _daily_data_df[proj]['date']= pd.to_datetime(_daily_data_df[proj]['date'])
    return {'cnf':_configuration,'daily_data':_daily_data_df,'entries':len(_daily_data_df[proj])}
  

#-SIDEBAR LOGO------------------------------------------------------------------------
def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def build_markup_for_logo(png_file,background_position="100% 100%",margin_top="100%",image_width="80%",image_height="33%"):
    binary_string = get_base64_of_bin_file(png_file)
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    padding-top: 100px;
                    background-size: %s %s;
                }
            </style>
            """ % (binary_string,image_width,image_height)

def add_logo(png_file):
    logo_markup = build_markup_for_logo(png_file)
    st.markdown(
        logo_markup,
        unsafe_allow_html=True,
    )


#-----------------------------------------------------------------------------------------------------------
#build main page  
st.set_page_config(layout="wide")

#load data
d = load_data()
# store project names from provided dict by fnc load_data
projectsName = list(d['daily_data'].keys())

target_proj = projectsName[0]
i_dt_obj, e_dt_obj = str(d['daily_data'] [target_proj]['date'].iloc[0]),str(d['daily_data'] [target_proj]['date'].iloc[-1])
i_dt_obj, e_dt_obj = datetime.datetime.strptime(i_dt_obj, "%Y-%m-%d %H:%M:%S"),datetime.datetime.strptime(e_dt_obj, "%Y-%m-%d %H:%M:%S")

#get active_features from config file
active_features =[af for af in list(d['cnf']['FEATURES'].keys()) if d['cnf']['FEATURES'][af]==True][2::]
active_features.insert(0,'date')

#computes required resources for WHOLE PERIOD zero carbon emission balance
prj = d['cnf']['PROJECTS']['00']  #<--- cfr assimilate-2.py
cumulated_emmissions = d['daily_data'][prj]['emissions_cumsum'].iloc[-1]
trees_to_plant_min  = "{0:3.0f}".format(cumulated_emmissions/d['cnf']['CARBON_BALANCE']['tree_co2kg_ratio_min'])
trees_to_plant_max  = "{0:3.0f}".format(cumulated_emmissions/d['cnf']['CARBON_BALANCE']['tree_co2kg_ratio_max'])
area_needed = "{0:3.0f}".format(10000*(cumulated_emmissions/d['cnf']['CARBON_BALANCE']['tree_co2kg_ratio_min']) / d['cnf']['CARBON_BALANCE']['trees_per_hectare_avg'])





#-----------------------------------------------------------------------------------------------------------
# #build page layout
#-----------------------------------------------------------------------------------------------------------
#configure Sidebar
#add_logo("./resources/Logo Innovation Lab (Corporate).png")    
add_logo("./resources/LogoSisalVerde.png")
with st.sidebar:
    from st_pages import Page, show_pages, add_page_title, Section
    show_pages(
    [
        Page("streamlit_app/main_page.py", "Home", "🏠"),
        Page("streamlit_app/pages/Data_Loader.py", "DATA LOADER" ,"⚙️"),
        Page("streamlit_app/pages/Logistic_regression.py", "LOGISTIC REG." ,"⚙️"),
        Page("streamlit_app/pages/XGBoost_model.py", "XG BOOSTER" ,"⚙️"),
        Page("streamlit_app/pages/map.py", "    MAP" ,"🦚"),
        
    ]
)


#containers for applogo (left) and data summary (right)
col1, col2 = st.columns([3, 1])
#render column 
with col1: 
    main_clicked =  insert_clickable_image(image_file = "resources/forest0_strip.png", title= "EMISSION TRACKER ver. "+str(__version__).zfill(2), size= 350, justification='center')

#render summary colum 
with col2:
    with st.container(): #row 0 - LEFT TITLE
        s = '<head><style>h1 {text-align: center;} 2 {text-align: left;} h3 {text-align: center;}</style></head>'
        st.markdown(s+'<h1>CARBON BALANCE</h1><p><h3> Y E A R  L Y </h3>', unsafe_allow_html=True)
    with st.container(): #row 1 - NUMBER OF TREES to ZERO BALANCE
        col210, col220 = st.columns([1,3])
        with col210:    tree_clk = insert_clickable_image(image_file = "resources/trees.png", title= "NUMBER OF TREES to ZERO BALANC", size= 50, justification='right')
        with col220:    st.markdown('<h1>'+trees_to_plant_min+' - '+trees_to_plant_max+'</h1>', unsafe_allow_html=True)
    with st.container(): #row 2 - PARCEL AREA FOR TREES to ZERO BALANCE
        col211, col221 = st.columns([1,3])
        with col211:    parcel_clk = insert_clickable_image(image_file = "resources/parcel.png", title= "PARCEL AREA FOR TREES to ZERO BALANCE", size= 50, justification='right')
        with col221:    st.markdown('<h1>'+area_needed+' m<sup style="font-size:.8em;">2</sup></h1>', unsafe_allow_html=True)

# Page span container 
with st.container(): #slider container
    slider = st.slider(':green[Select date range]', min_value=i_dt_obj, value=(i_dt_obj, e_dt_obj), max_value=e_dt_obj,  key='DateSlider')
with st.container(): #Metric container
           placeholders = st.columns(3)
           m0 = placeholders[0].empty()
           m1 = placeholders[1].empty()
           m2 = placeholders[2].empty()

#build interactive section
#create containers
with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1 :
        selected_projects = st.multiselect('Select the projects to show',projectsName,default=projectsName[-1],key='SelectedProjects_ms')
    with col2 : 
        y_ax_variable = st.selectbox('Select the dependent label (Vertical axis)',active_features[1::],key='Selected_y_lbl_ms')
    with col3 : 
        y_ax_variable = st.selectbox('Select the independent label  (Horizontal axis)',active_features,key='Selected_x_lbl_ms')
    with col4 : 
        opt_list = ['Linear','SemiLog Y', 'SemiLog X', 'LogLog']
        options = st.selectbox('Options',opt_list,key='Selected_opt_ms')
    with col5 : 
         use_cumulated_values = st.checkbox('Cumulated dist.')
if len(selected_projects) > 0:
        #get slider values
        res = st.session_state.DateSlider
        dict_projects_df_sliced={}
        for kw,proj in  d['daily_data'].items():
          dict_projects_df_sliced [kw]= subset_df(proj, column = 'date', values = res)
        #build data for metrics
        actual_data = {'emissions':{'label':'emissions', 'title': 'emissions', 'value': dict_projects_df_sliced['All_projects']['emissions_cumsum'].iloc[-1]},
                       'emissions_rate':{'label':'emissions rate', 'title': 'emissions rate', 'value': np.average(dict_projects_df_sliced['All_projects']['emissions_rate'])},
                       'energy_consumed':{'label':'energy consumed', 'title': 'energy_consumed', 'value': dict_projects_df_sliced['All_projects']['energy_consumed_cumsum'].iloc[-1]}
                      }
        
        reference_data = {'emissions':{'label':'emissions', 'title': 'emissions', 'value': d['daily_data']['All_projects']['emissions_cumsum'].iloc[-1]},
                       'emissions_rate':{'label':'emissions rate', 'title': 'emissions rate', 'value': np.average(d['daily_data']['All_projects']['emissions_rate'])},
                       'energy_consumed':{'label':'energy consumed', 'title': 'energy_consumed' , 'value': d['daily_data']['All_projects']['energy_consumed_cumsum'].iloc[-1]}
                      }
        keys = ['emissions', 'emissions_rate', 'energy_consumed']
        update_metrics(placeholders, actual_data, reference_data, keys, decimals = 2)

        #Parse user options
        sel_yax_lbl = st.session_state.Selected_y_lbl_ms
        sel_xax_lbl = st.session_state.Selected_x_lbl_ms
        opts = st.session_state.Selected_opt_ms
        yax_lbl = sel_yax_lbl
        xax_lbl = sel_xax_lbl
        if not use_cumulated_values:       
            if 'Linear' in opts : 
                yax_lbl = sel_yax_lbl
                xax_lbl = sel_xax_lbl
            elif 'SemiLog Y' in opts : 
                yax_lbl=sel_yax_lbl+'_log'
            elif 'SemiLog X' in opts : 
                if sel_xax_lbl != 'date':
                    xax_lbl=sel_xax_lbl+'_log'
            elif 'LogLog' in opts : 
                yax_lbl=sel_yax_lbl+'_log'
                if sel_xax_lbl != 'date':
                    xax_lbl=sel_xax_lbl+'_log'
        if use_cumulated_values:       
            if 'SemiLog Y' in opts : 
                yax_lbl=sel_yax_lbl+'_log_cumsum'
            elif 'SemiLog Y' not in opts :      
                yax_lbl=sel_yax_lbl+'_cumsum'
            elif 'SemiLog X' in opts : 
                if sel_xax_lbl != 'date':
                   xax_lbl=sel_xax_lbl+'_log_cumsum'
            elif 'SemiLog X' not in opts :      
                  if sel_xax_lbl != 'date': xax_lbl=sel_xax_lbl+'_cumsum'
            elif 'LogLog' in opts : 
                yax_lbl=sel_yax_lbl+'_log_cumsum'
                if sel_xax_lbl != 'date': xax_lbl=sel_xax_lbl+'_log_cumsum'
            elif 'LogLog' not in opts : 
                yax_lbl=sel_yax_lbl+'_cumsum'
                if sel_xax_lbl != 'date': xax_lbl=sel_xax_lbl+'_cumsum'

        #build temp dataframe for charting 
        t_df = dict_projects_df_sliced[selected_projects[0]][[xax_lbl]] #take indipendet var from first proj
        for proj in selected_projects:
            t_df[proj]= dict_projects_df_sliced[proj][yax_lbl]
# Chart rendering        
with st.container():
    if  len(selected_projects) >0 :    
        if xax_lbl == 'date':
            fig = px.scatter(t_df, 
                            x=xax_lbl, y=selected_projects,  
                            marginal_y="box",
                            template="simple_white")
        else : 
            fig = px.scatter(t_df, 
                            x=xax_lbl, y=selected_projects,  
                            marginal_y="box",
                            marginal_x="box", 
                            trendline="ols", 
                            template="simple_white")
                  
        st.plotly_chart(fig,  use_container_width=True)
               
        

