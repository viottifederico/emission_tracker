import pandas as pd
import numpy as np
import random
import geopandas as gpd
import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from support import *


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
   #make color palette for polygons fill
   palette = makePalette(colors = ['#F7FCBD','#CFE2F3','#B6D7A8','#6AA84F' ], bins = 10)    
   return d,palette

st.set_page_config(layout="wide")
geography_data = "./data_raw/limits_P_15_municipalities.geojson"
_data,palette=make_data(geojson_filename=geography_data)   

def stfunc (f,palette=palette):
             intervals = np.array(list(palette.keys()))
             i = np.where( intervals >= f['properties']['trees'])[0]
             style = {
                 "fillColor": palette[intervals[i[0]]],
                 "fillOpacity": opacity/100,
                 "weight": 0.8,
                 "color": '#f7fcbd'}
             return style
    
# print('\n--')
with st.form('my form'):
   st.container()
   col1,col2 = st.columns([3,1])
   with col2:
      sbmt = st.form_submit_button(label="Submit", help=None, on_click=None) 
      global opacity   
      opacity = st.slider('Transparency', 0, 100, 50,key="slider_transparency")
      BkMapStype = st.selectbox('Select the background map',('Cartodb Positron', 'OpenStreetMap', 'Cartodb dark_matter'), index= 0)
      #creates folium map
      m = folium.Map(location=[45.4668, 9.1905], zoom_start=10,tiles=BkMapStype)
   # TO DO :: ADD LOGIC TO SWITCH FROM HEAT MAP and POLYGONS, possibly some data preproc is required 
   # #  HeatMap(_data,radius = 50, gradient={.01: '#F7FCBD', .25: '#CFE2F3', .5: '#B6D7A8', 0.95: '#6AA84F'}).add_to(m)
      #colored polygonsa
      geo_j = folium.GeoJson(data=_data, style_function = stfunc)
      geo_j.add_to(m)      

   with col1:
      #show folium object
      st_data = st_folium(m, width= "100%")



     