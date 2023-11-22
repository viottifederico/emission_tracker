import streamlit as st
from datetime import date
import pandas as pd
st.set_page_config(layout="wide")
st.title("XGBoost model")


df = pd.read_csv("./assimilated_data/XGBoost model.csv")
df = df.drop(columns= ['project_name','timestamp','Unnamed: 0'])


# with st.container():
#     col1,col2,col3,col4 = st.columns(4)
#     col1.metric(label="duration", value=df["duration"].round(2), delta="5")
#     col2.metric(label="emissions", value=df["emissions"].round(2), delta="1.2")
#     col3.metric(label="emissions_rate", value=df["emissions_rate"].round(2), delta="-3.8")
#     col4.metric(label="cpu_power", value=df["cpu_power"].round(2), delta="2.4")

# with st.container():
#     col5,col6,col7,col8 = st.columns(4)
#     col5.metric(label="ram_power", value=df["ram_power"].round(2), delta="-12.5")
#     col6.metric(label="cpu_energy", value=df["cpu_energy"].round(2), delta="-7.4")
#     col7.metric(label="ram_energy", value=df["ram_energy"].round(2), delta="2.9")
#     col8.metric(label="energy_consumed", value=df["energy_consumed"].round(2), delta="6.3")
    
st.subheader("Series Data:")
st.dataframe(df, hide_index=True)