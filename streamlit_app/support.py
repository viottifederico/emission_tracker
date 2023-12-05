import datetime,calendar, yaml 
import numpy as np
import base64

import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer 
from st_clickable_images import clickable_images

import pandas as pd

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




def hex_to_RGB(hex):
  ''' "#FFFFFF" -> [255,255,255] '''
  # Pass 16 to the integer function for change of base
  return [int(hex[i:i+2], 16) for i in range(1,6,2)]

def RGB_to_hex(RGB):
  ''' [255,255,255] -> "#FFFFFF" '''
  # Components need to be integers for hex to make sense
  RGB = [int(x) for x in RGB]
  return "#"+"".join(["0{0:x}".format(v) if v < 16 else
            "{0:x}".format(v) for v in RGB])

def color_dict(gradient):
  ''' Takes in a list of RGB sub-lists and returns dictionary of
    colors in RGB and hex form for use in a graphing function
    defined later on '''
  return {"hex":[RGB_to_hex(RGB) for RGB in gradient],
      "r":[RGB[0] for RGB in gradient],
      "g":[RGB[1] for RGB in gradient],
      "b":[RGB[2] for RGB in gradient]}


def linear_gradient(start_hex, finish_hex="#FFFFFF", n=10):
  ''' returns a gradient list of (n) colors between
    two hex colors. start_hex and finish_hex
    should be the full six-digit color string,
    inlcuding the number sign ("#FFFFFF") '''
  # Starting and ending colors in RGB form
  s = hex_to_RGB(start_hex)
  f = hex_to_RGB(finish_hex)
  # Initilize a list of the output colors with the starting color
  RGB_list = [s]
  # Calcuate a color at each evenly spaced value of t from 1 to n
  for t in range(1, n):
    # Interpolate RGB vector for color at the current value of t
    curr_vector = [
      int(s[j] + (float(t)/(n-1))*(f[j]-s[j]))
      for j in range(3)
    ]
    # Add it to our list of output colors
    RGB_list.append(curr_vector)
  return color_dict(RGB_list)

def makePalette(colors,bins):
    """_summary_
    Creates a color palette given n colors and a 
    Args:
        colors (_type_): array or RGB colors ['#12ABF3","#AABBDD"]
        bins (_type_): number of bins for each step step = len(colors)-1
    """
    palette=[]
    for i in range(len(colors)-1):
        palette.append(linear_gradient(start_hex=colors[i], finish_hex=colors[i+1], n=bins))
    # queuing palette chunks.
    array = palette[0]['hex']
    for i in palette[1::] : array.extend(i['hex'][1::])    
    k = np.linspace(0,1,len(array))
    palette = {float("{0:.3f}".format(k[i])):array[i] for i in range(len(array))}
    return  palette



def build_subpage(streamlit_obj, title,df_csv):
    """_summary_

    Args:
        streamlit_obj (_type_): _description_
        title (_type_): _description_
        df_csv (_type_): _description_
    """
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
    


def update_metrics(placeholders, actual_data, reference_data, keys, decimals = 2):
    """_summary_

    Args:
        placeholders (list): list of streamlit columns object
        actual_data (dict): actual data {key:{label: str, title: str, value: numeric }} see example
        reference_data (): ref data {key:{label: str, title: str, value: numeric }} see example
        keys (list):sorted list must match dictionary 0 level keys
        
        dictionary example : 
        {
         'emissions':{'label':'Emissions', title:'EMISSIONS, 'value':1234.4321},
         'energy consumed':{'label':'Energy consumed', title:'CONSUMED NRGY, 'value':5678.321} 
        }
    """
    for i,placeholder in enumerate(placeholders):
        keyw = keys[i] 
        actual_element =  actual_data[keyw]
        ref_element = reference_data[keyw] 
        act_value = round(actual_element['value'],2)
        act_label = actual_element['label'].upper()
        act_title  = actual_element['title']
        ref_value = round(ref_element['value'],2)
        ref_label = ref_element['label'].upper()
        ref_title  = ref_element['title']
        v = str(100*round(act_value/ref_value,decimals))+' %'
        placeholder.metric(label=act_label.upper(), value=act_value, delta=v)

'''
 Image tools
'''
def img_to_bytes(img_path):
    """_summary_
    Read local image file and returns its bytes repr (required to insert an image in streamlit markdown html)

    Args:
        img_path (str): local image filename

    Returns:
        str: encoded image
    """
    with open(img_path, 'rb') as f:
         img_bytes = f.read()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def insert_clickable_image(image_file, title= "", size= 100, justification='center'):
    """_summary_
    
    Insert a clickable image in stramlit container 

    Args:
        image_file (str, required): local image file
        title (str, optional): image caption, also it is the tooltip. Defaults to "".
        size (int, optional): image size Defaults to 100.
        justification (str, optional): image location. Defaults to 'center'.

    Returns:
        obj: image title if clicked
    """
    images = []
    for file in [image_file]:
        with open(file, "rb") as image:
              encoded = base64.b64encode(image.read()).decode()
              images.append(f"data:image/jpeg;base64,{encoded}")

    clicked = clickable_images(images,titles=[title],
                                       div_style={"display": "flex", "justify-content": justification, "flex-wrap": "wrap"},
                                       img_style={"margin": "5px", "height": str(size)+"px"},)
    return clicked


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
    datetime_arr = daily_df_dict[projectName]['date']
    return arr,datetime_arr


def subset_df(df, column='date', values=None):

    """subset a dataframe given column name and boundary values

    Args:
        df (DataFramem):Pandas dataframe
        column (str): column name, must exists in  df
        values (same as df.column): boundary values of the same type of df.column

    Returns:
        DataFrame : subset of original df
    """
    out = df[(df[column] > values[0]) & (df[column]< values[1])]
    print ('-> subset_df ::', out[column].iloc[0], type(out[column].iloc[0]),out[column].iloc[-1], type(out[column].iloc[-1]), )
    return out
