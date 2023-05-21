import folium
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pyproj import Transformer
import numpy as np

def visualize_airport_map(df,  zoom):
    
    lat_map=30.038557
    lon_map=31.231781
    f = folium.Figure(width=1000, height=500)
    m = folium.Map([lat_map,lon_map], zoom_start=zoom).add_to(f)
    folium.Marker(location=[df["REF_POINT_LAT"].iloc[0],df["REF_POINT_LONG"].iloc[0]],icon=folium.Icon(icon_color='white',icon ='plane',prefix='fa')).add_to(m)
    
    folium.Marker(location=[df["RUN1_LAT_START"].iloc[0],df["RUN1_LONG_START"].iloc[0]],icon=folium.Icon(icon_color='white',icon ='plane',prefix='fa')).add_to(m)
    folium.Marker(location=[df["RUN2_LAT_START"].iloc[0],df["RUN2_LONG_START"].iloc[0]],icon=folium.Icon(icon_color='white',icon ='plane',prefix='fa')).add_to(m)
    
    folium.Marker(location=[df["RUN1_LAT_END"].iloc[0],df["RUN1_LONG_END"].iloc[0]],icon=folium.Icon(icon_color='white',icon ='plane',prefix='fa')).add_to(m)
    folium.Marker(location=[df["RUN2_LAT_END"].iloc[0],df["RUN2_LONG_END"].iloc[0]],icon=folium.Icon(icon_color='white',icon ='plane',prefix='fa')).add_to(m)
    
    return m

def visualize_flight(dfairp, zoom, dfflight):
    lat_map=30.038557
    lon_map=31.231781
    f = folium.Figure(width=1000, height=500)
    m = folium.Map([lat_map,lon_map], zoom_start=zoom).add_to(f)
   
    #folium.Marker(location=[dfairp["REF_POINT_LAT"].iloc[0],dfairp["REF_POINT_LONG"].iloc[0]],icon=folium.Icon(icon_color='white',icon ='plane',prefix='fa')).add_to(m)
        
    # Extract the coordinates from the DataFrame and add a trace line
    #dfflight["LATITUDE"] = dfflight["LATITUDE"] - 4.143478
    #dfflight["LONGITUDE"] = dfflight["LONGITUDE"] + 23.7672
    latlon = dfflight[['LATITUDE', 'LONGITUDE']].values.tolist()
    folium.PolyLine(latlon, weight=2.5, opacity=1).add_to(m)

    for i in range(len(dfflight)):
        folium.Marker(location=[dfflight["LATITUDE"].iloc[i],dfflight["LONGITUDE"].iloc[i]],icon=folium.Icon(icon_color='white',icon ='circle-dot',prefix='fa')).add_to(m)
        
    return m

def create_map(flight, airport):
   
    # Create a 3D scatter plot for the runways
    run1 = go.Scatter3d(
            x=[airport["RUN1_LAT_START"].iloc[0], airport["RUN1_LAT_END"].iloc[0]],
            y=[airport["RUN1_LONG_START"].iloc[0], airport["RUN1_LONG_END"].iloc[0]],
            z=[airport["ELEVATION"].iloc[0], airport["ELEVATION"].iloc[0]],
            mode='lines',
            name='Runway 1 - 08L/26R',
            line=dict(color='black', width=20)
        )
    run2 = go.Scatter3d(
            x=[airport["RUN2_LAT_START"].iloc[0], airport["RUN2_LAT_END"].iloc[0]],
            y=[airport["RUN2_LONG_START"].iloc[0], airport["RUN2_LONG_END"].iloc[0]],
            z=[airport["ELEVATION"].iloc[0], airport["ELEVATION"].iloc[0]],
            mode='lines',
            name='Runway 2 - 08R/26L',
            line=dict(color='grey', width=20)
        )
    
    before_flight = flight[flight["RUN"] == "BEFORE"]
    on_flight = flight[flight["RUN"] == "ON"]
    after_flight = flight[flight["RUN"] == "AFTER"].head(10)

    trace_before = go.Scatter3d(
        x= before_flight["LATITUDE"], y= before_flight["LONGITUDE"], z= before_flight["Altitude"],
        mode = 'lines', line = dict(width=3, color='red'), name = "Trajectory before reaching runway"
    )

    trace_on = go.Scatter3d(
        x=on_flight["LATITUDE"], y=on_flight["LONGITUDE"], z=on_flight["Altitude"],
        mode = 'lines', line = dict(width=3, color='green'), name = "Runway roll"
    )

    trace_after = go.Scatter3d(
        x=after_flight["LATITUDE"], y=after_flight["LONGITUDE"], z=after_flight["Altitude"],
        mode = 'lines', line = dict(width=1, color='blue'), name = "After passing runway end (not considering FL)"
    )

    data = [run1, run2, trace_before, trace_on, trace_after]
    fig = go.Figure(data=data)

    # Set layout options
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Latitude'),
            yaxis=dict(title='Longitude'),
            zaxis=dict(title='Elevation (ft)'),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.5)
        ),
        title='Bucharest Airport (LROP) 3D Map with 1 WizzAir Flight'
    )

    return fig

def runways_trace(lrop):
    local_projection = 'epsg:32635'

    # Instantiate a Transformer
    transformer = Transformer.from_crs('epsg:4326', local_projection)
    lrop['RUN1_LAT_START_tr'], lrop["RUN1_LONG_START_tr"] = transformer.transform(lrop['RUN1_LAT_START'].values, lrop["RUN1_LONG_START"].values)
    lrop["RUN1_LAT_END_tr"], lrop["RUN1_LONG_END_tr"] = transformer.transform(lrop["RUN1_LAT_END"].values, lrop["RUN1_LONG_END"].values)

    lrop['RUN2_LAT_START_tr'], lrop["RUN2_LONG_START_tr"] = transformer.transform(lrop['RUN2_LAT_START'].values, lrop["RUN2_LONG_START"].values)
    lrop["RUN2_LAT_END_tr"], lrop["RUN2_LONG_END_tr"] = transformer.transform(lrop["RUN2_LAT_END"].values, lrop["RUN2_LONG_END"].values)

    line_color = 'rgba(0, 0, 0, 0.3)'
    runway_trace_1 = go.Scatter(
        x=[lrop['RUN1_LAT_START_tr'].iloc[0], lrop['RUN1_LAT_END_tr'].iloc[0]],
        y=[lrop['RUN1_LONG_START_tr'].iloc[0], lrop['RUN1_LONG_END_tr'].iloc[0]],
        mode='lines',
        line=dict(color='black', width=8)
    )
    runway_trace_1.line.color = line_color

    runway_trace_2 = go.Scatter(
        x=[lrop['RUN2_LAT_START_tr'].iloc[0], lrop['RUN2_LAT_END_tr'].iloc[0]],
        y=[lrop['RUN2_LONG_START_tr'].iloc[0], lrop['RUN2_LONG_END_tr'].iloc[0]],
        mode='lines',
        line=dict(color='black', width=8)
    )
    runway_trace_2.line.color = line_color

    return runway_trace_1, runway_trace_2

def sound_dispersion_plot(x, y, total_sound_level_db, lrop):

    custom_colors = [
        [0.0, 'rgba(0, 0, 128, 0.01)'],     # Dark blue with 50% opacity at 0.0
        [0.25, 'rgba(0, 0, 255, 0.11)'],     # Blue with 80% opacity at 0.25
        [0.5, 'rgba(0, 255, 255, 0.2)'],    # Cyan with 50% opacity at 0.5
        [0.75, 'rgba(255, 255, 0, 1)'],   # Yellow with 80% opacity at 0.75
        [1.0, 'rgba(255, 0, 0, 1)']       # Red with 50% opacity at 1.0
        ]
    contour_trace = go.Contour(
        x=x, 
        y=y,
        z=total_sound_level_db,
        colorscale= custom_colors,
        colorbar=dict(
            title='Sound Pressure Level (dB)',
            titleside='right',
        )
    )
    fig = go.Figure()
    fig.add_trace(contour_trace)

    runway_trace_1, runway_trace_2 = runways_trace(lrop)
    fig.add_trace(runway_trace_1)
    fig.add_trace(runway_trace_2)

    fig.update_layout(
        title='Sound Dispersion Map',
        xaxis=dict(title='Longitude'),
        yaxis=dict(title='Latitude')
    )
    return fig


def sliding_bar(objects, x, y):

    X, Y = np.meshgrid(x, y)
    frames = []
    for idx, object_info in enumerate(objects):

        # Position and intensity of sound source
        object_pos = np.array(object_info[:2])
        intensity = object_info[2]  # dB

        # Convert dB to a linear scale for calculations
        intensity_linear = 10**(intensity / 10)

        # Calculate Euclidean distance from each point in the space to the sound source
        distance = np.sqrt((X - object_pos[0])**2 + (Y - object_pos[1])**2)

        # Apply inverse square law
        sound_level = intensity_linear / (4*np.pi*distance**2)

        # Convert the result back to dB for visualization
        sound_level_db = 10 * np.log10(sound_level)

        # Create the trace for the 2D heatmap
        contour_trace = go.Contour(
            z=sound_level_db, 
            x=x, 
            y=y,
            colorscale='jet',
            colorbar=dict(
                title='Sound Pressure Level (dB)',
                titleside='right'),
            #showscale=False,
            visible=(idx==0) # Only the first frame is visible
        )

        frames.append(contour_trace)

    # Add a slider to switch frames
    steps = []
    for i, frame in enumerate(frames):
        step = dict(method="update", label = f'Object {i+1}', 
                    args=[{"visible": [el==i for el in range(len(frames))]},
                        {"title": f"Sound Dispersion Map for Object {i+1}"}])
        steps.append(step)
    sliders = [dict(steps=steps)]

    fig = go.Figure(data=frames, layout={'sliders': sliders})
    fig.update_layout(
        title='Sound Dispersion Map for different position',
        xaxis=dict(title='Longitude'),
        yaxis=dict(title='Latitude'))

    return fig
    



