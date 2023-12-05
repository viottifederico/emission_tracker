
import pandas as pd
import geopandas as gpd
import numpy as np
import random
import numpy as np

def make_data():
   filename = "./data_raw/limits_P_15_municipalities.geojson"
   fobj = open(filename)
   d =  gpd.read_file(fobj)
   for i in range(len(d)):
      print(i,d.name.iloc[i])
   s = [random.randint(0, 100)/100 for v in range(len(d))]
   d.insert(0,"trees",s)
   _data= []
   for i in range(len(d)):
      k = [d['geometry'].iloc[i].centroid.y,d['geometry'].iloc[i].centroid.x,d['trees'].iloc[i]]
      _data.append(k)
   print (_data)   
   df = pd.DataFrame(_data, columns = ['Latitude', 'Longitude', 'Value']) 
   df.to_csv('./assimilated_data/trees.csv', index = False)

make_data()      