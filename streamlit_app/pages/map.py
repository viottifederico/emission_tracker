import pandas as pd
import numpy as np
import random
import geopandas as gpd
import folium
from folium.plugins import TimestampedGeoJson
import time
import streamlit as st
from streamlit_folium import st_folium
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from folium.plugins import HeatMap
import streamlit.components.v1 as com 
from support import *

#-SIDEBAR LOGO------------------------------------------------------------------------
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

print ('\n\n--------------\n\n')

global colors
global palette
global opacity

st.showWarningOnDirectExecution = False

def make_data(geojson_filename = None):
   """"
   Preprocess data 
   add random feature : planted trees
   """
   fobj = open(geojson_filename)
   d =  gpd.read_file(fobj)
   #fake feature
   planted_trees = [random.randint(0, 100)/100 for v in range(len(d))]
   d.insert(0,"trees",planted_trees)
   #get centroids for then heatmap
   d.insert(0,'Latitude',d['geometry'].centroid.y)
   d.insert(0,'Longitude',d['geometry'].centroid.x)
   d.to_csv('test.csv')
   return d

def stfunc (f):
             intervals = np.array(list(palette.keys()))
             i = np.where( intervals >= f['properties']['trees'])[0]
             style = {
                 "fillColor": palette[intervals[i[0]]],
                 "fillOpacity": opacity/100,
                 "weight": 0.8,
                 "color": '#f7fcbd'}
             return style
    
def show_map(m):
    st_data = st_folium(m, width= "100%")

def refresh_page():
     st.rerun()

st.container()
st.markdown('<h1> Planted trees </h1>',unsafe_allow_html=True)

with st.form('my form'):
    st.container()
    col1,col2 = st.columns([3,1])
    with col2:
        sbmt = st.form_submit_button(label="Refresh map", help='Click to apply changes and refresh the map', on_click=None) 
        opacity = st.slider('Select Transparency', 0, 100, 50,key="slider_transparency")
        st.container()
        st.text('Select colors for solid and gradient')
        col00,col33,col66,col100 = st.columns([1,1,1,1])
        with col00:            
              c0 = st.color_picker('0%', '#F7FCBD', key='c0')
        with col33:            
              c1= st.color_picker('33%', '#CFE2F3', key='c1')
        with col66:            
              c2 = st.color_picker('66%', '#B6D7A8', key='c2')
        with col100:           
              c3 = st.color_picker('100%', '#6AA84F', key='c3')
        BkMapStyle = st.selectbox('Select the background map',('Cartodb Positron', 'OpenStreetMap', 'Cartodb dark_matter'), index= 0)
        MapType = st.selectbox('Select the Map type map',('Colored polygons', 'Heatmap', 'Animation'), index= 0)
        if MapType == 'Animation':
             col200,col210 = st.columns([1,1])
             with col200 : 
                 AnimationFeatureFillColor = st.color_picker('Feature color', '#6AA84F', key='AniFeatFillColor')
             with col210: 
                 AnimationPointSize = st.slider('Marker size', 0, 100, 5)    

             
       # create dataframe for mapping
        geography_data = "./data_raw/limits_P_15_municipalities.geojson"
        _data=make_data(geojson_filename=geography_data)   
        palette = makePalette(colors = [c0,c1,c2,c3], bins = 10)    
        
 
    with col1:
        #creates folium map
        keywords={'timeDimensionControl':False}
        m = folium.Map(location=[45.4668, 9.1905], zoom_start=10,tiles=BkMapStyle,**keywords)
        #colored polygonsa
        if MapType == 'Colored polygons':
            geo_j = folium.GeoJson(data=_data, style_function = stfunc)
            geo_j.add_to(m)      
        #heatmap
        elif   MapType == 'Heatmap':
            # print({.01: c0, .25: c1, .5: c2, 0.999: c3},'\n',_data.keys())
            LA = np.array(_data['Latitude'])
            LO = np.array(_data['Longitude'])
            V = np.array(_data['trees'])
            HeatMap(data=np.vstack([np.vstack([LA,LO]),V]).T,radius = 50,gradient={0.01: c0, 0.33: c1, 0.66: c2, 0.999: c3}).add_to(m)
        #animation  
        elif MapType == 'Animation':   
            def create_animation_data_with_timeline( Y,M,D,h,m,s, df, value_column):
                """
                Provides a subset of input datadframe [df] using given column_values 
                adding a timeline scaled to days to be used with TimestampedGeoJson
   
                Remarks : input dataframe MUST have columns labelled "Latitude", "Longitude"
   
                Args:
                    Y (int): year i.e.  2023
                    M (int): month i.e. 11
                    D (int): day i.e.   13
                    h (int): hour i.e   12
                    m (int): minute i.e. 24
                    s (int): second i.e. 0
                    days (int): sumbe of days after the given date
                    df (pandas dataframe): input dataframe
                    value_column (str): i.e. 'trees'
   
                
                Returns:
                    Pandas dataframe with colums Latitude, Longitude, Count, Timeline            
                """
                #create data structure for the animation           
                adate = datetime.datetime(Y,M,D,h,m,s)
                ldate =[]
                for i in range(len(df)): 
                    adate +=datetime.timedelta(days=1)
                    ldate.append(adate.isoformat())
                df.insert(0,'AnimationTimestamp', ldate)    
                #dataframe with needed labels
                animation_data = pd.DataFrame({
                                'Latitude': df['Latitude'],
                                'Longitude': df['Longitude'],
                                'Count': df[value_column],
                                'Timeline': df['AnimationTimestamp']})
                return animation_data
            def create_geojson_features(data = None, fill_color = None, markerSize=None):
                """provides the GeoJson for animation

                Args:
                    data (dataframe): it is the output of create_animation_data_with_timeline

                Returns:
                    list: fit for : TimestampedGeoJson{'features': features}
                """
                features = []
                for _, row in data.iterrows():
                    feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type':'Point',
                            'coordinates':[row['Longitude'],row['Latitude']]},
                        'properties': {
                            'time': row["Timeline"],
                            'style': {'color': fill_color},
                            'icon': 'circle',
                            'iconstyle':{
                                'fillColor': fill_color,
                                'fillOpacity': 1,
                                'stroke': 'true',
                                'radius': row["Count"]*markerSize/10
                           }
                       }
                    }     
                    features.append(feature)
                return features
            features = create_geojson_features(data= create_animation_data_with_timeline(Y = 2023,
                                                                                         M= 11,
                                                                                         D= 13,
                                                                                         h=12,
                                                                                         m=24,
                                                                                         s=0,
                                                                                         df = _data,
                                                                                         value_column = 'trees'),
                                                fill_color =  AnimationFeatureFillColor,
                                                markerSize = AnimationPointSize)
                                            
            #invoke animationmethod
            keywords = {'timeDimensionControl': False}
            TimestampedGeoJson(
                {'type': 'FeatureCollection',
                'features': features}
                , period='P1D'
                , transition_time=100
                , auto_play=True
                
                # , add_last_point=True
                # , max_speed=5
                # , loop=True
                # , loop_button=False
                # , time_slider_drag_update=False
                ).add_to(m)

        #publish folium object (map) to the page 
        st_data = st_folium(m,   height=500,    width='100%')

#footer
st.container()
s = '<hr><div class="row"><div class="col-md-8 col-sm-6 col-xs-12"><p class="copyright-text">SISAL - INNOVATION LAB - 2023</p></div></div>'
st.markdown(s, unsafe_allow_html=True)         
           
        
 
 
       