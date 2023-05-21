import pandas as pd
import streamlit as st
import sys
import folium
from pyproj import Transformer
import plotly.graph_objects as go
from streamlit_folium import folium_static
sys.path.append('classes')
#sys.path.append("dataset")

from classes.plots import visualize_airport_map, visualize_flight, create_map, sound_dispersion_plot, sliding_bar
from classes.data import lrop_data
from classes.calculations import create_flight_object, coordinate_objects, create_mesh, sound_dispersion

st.set_page_config(page_title = 'Noise Tool', layout = "wide")
st.header("Noise Tool")
st.subheader("Deliverable 1 - Noise dispersion study (departure only) for A320 at LROP using NPD and FlightRadar24 data")

uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True, type =['csv'])
for uploaded_file in uploaded_files:
     #bytes_data = uploaded_file.read()
     #st.write("filename:", uploaded_file.name)
     if(uploaded_file.name == 'NPD_data.csv'):
        in1 = pd.read_csv(uploaded_file, sep=";")
        st.write("NPD data OK!")
     else:
        in2 = pd.read_csv(uploaded_file)
        st.write("Flight data OK!")

#@st.experimental_memo()
@st.cache_resource
def Simulation():

    npd_data = in1.copy(deep = True)
    #npd_data = pd.read_csv("./dataset/NPD_data.csv", sep=";")
    lrop = lrop_data()
    
    ## - WizzAir flight
    #flight = pd.read_csv("./dataset/W63003_3059933c.csv")
    flight = in2.copy(deep = True)
    flight[["LATITUDE", "LONGITUDE"]] = flight["Position"].str.split(',', expand=True)
    flight["LATITUDE"] = flight["LATITUDE"].astype(float)
    flight["LONGITUDE"] = flight["LONGITUDE"].astype(float)


    flight = create_flight_object(lrop, flight, npd_data)
    airp_map = visualize_airport_map(lrop, 1)
    flight_traj_folium =  visualize_flight(lrop, 1, flight)
    flight_3d_traj = create_map(flight, lrop)

    def create_dispersion_plot(flight_data, lrop, bool_interpolate):
        objects = coordinate_objects(flight_data, bool_interpolate)
        x, y = create_mesh()
        total_sound_level_db = sound_dispersion(x, y, objects)
        fig = sound_dispersion_plot(x, y, total_sound_level_db, lrop)
        
        return fig

    fig_1 = create_dispersion_plot(flight[flight["RUN"] == "BEFORE"], lrop, False)
    fig_2 = create_dispersion_plot(flight[flight["RUN"] == "ON"], lrop, True)
    fig_3 = create_dispersion_plot(flight.iloc[47:80], lrop, True)



    objects_bar = coordinate_objects(flight[flight["RUN"] == "ON"], False)
    x, y = create_mesh()
    fig_4 = sliding_bar(objects_bar, x, y)


    return lrop, airp_map, flight_traj_folium, flight_3d_traj, fig_1, fig_2, fig_3, fig_4
    #return lrop, airp_map

load = st.checkbox("Start calculating")
if(load):
    lrop, airp_map, flight_traj_folium, flight_3d_traj, fig_1, fig_2, fig_3, fig_4 = Simulation()
    #lrop, airp_map = Simulation()
    st.write("Airport Data - " + lrop["APT_ID"].iloc[0])
    st.table(lrop)
    with st.expander("Airport and flight data"):
        st.subheader("Airport location and runways")
        folium_static(airp_map)
       
        st.subheader("Trajectory of the WizzAir flight")
        folium_static(flight_traj_folium)

        st.subheader("3D Trajectory of the flight")
        st.plotly_chart(flight_3d_traj)

    with st.expander("Noise contour map (in local coordinates)"):
        st.write("Select area to zoom")
        st.subheader("Sound dispersion - TAXI")
        st.plotly_chart(fig_1)

        st.subheader("Sound dispersion - RUNWAY ROLL + TAKE-OFF")
        st.plotly_chart(fig_2)

        st.subheader("Sound dispersion - RUNWAY ROLL + TAKE-OFF + INITIAL CLIMB")
        st.plotly_chart(fig_3)
    
    with st.expander("Noise contour for different times (Runway roll)"):
        st.plotly_chart(fig_4)

  

