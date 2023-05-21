import pandas as pd
from pyproj import Transformer
import numpy as np

# Creates data for the flight subjective to the airport -> calculates TOF time 
def create_flight_object(dfairp, dfflight, npd_data):
    # ------- Add column that shows the flight phase
    # It is considered runway 1
    # RUN -> "BEFORE" if latlon are before RUN1; "ON" if latlon ar between RUN1 coord. ; "AFTER" -> the other
    dfflight["RUN"] = "AFTER"
    i = 0
    while((dfflight["LATITUDE"].iloc[i] <= dfairp["RUN1_LAT_START"].iloc[0]) | (dfflight["LONGITUDE"].iloc[i] <= dfairp["RUN1_LONG_START"].iloc[0])):
        dfflight["RUN"].iloc[i] = "BEFORE"
        i = i+1
    print("first i is: ", i)
    # now i is the time when the aircraft reaches the runway
    while((dfflight["LATITUDE"].iloc[i] <= dfairp["RUN1_LAT_END"].iloc[0]) | (dfflight["LONGITUDE"].iloc[i] <= dfairp["RUN1_LONG_END"].iloc[0])):
        dfflight["RUN"].iloc[i] = "ON"
        i = i+1
    print("second i is: ", i)
    # the rest is after rolling on the runway
    # -----------------------------------------------

    # ----------- Merge it with NPD_data
    dfflight["L"] = 0
    npd_data_filt = npd_data[ (npd_data["Op Mode"] == "D") & (npd_data["Noise Metric"] == "LAmax") & (npd_data["Power Setting"] == 23000)]

    # check after --> altitude vs reference altitude
    dfflight["L"][dfflight["Altitude"] <= 25000] = npd_data_filt["L_25000ft"].iloc[0]
    dfflight["L"][dfflight["Altitude"] <= 16000] = npd_data_filt["L_16000ft"].iloc[0]
    dfflight["L"][dfflight["Altitude"] <= 10000] = npd_data_filt["L_10000ft"].iloc[0]
    dfflight["L"][dfflight["Altitude"] <= 6300] = npd_data_filt["L_6300ft"].iloc[0]
    dfflight["L"][dfflight["Altitude"] <= 4000] = npd_data_filt["L_4000ft"].iloc[0]
    dfflight["L"][dfflight["Altitude"] <= 2000] = npd_data_filt["L_2000ft"].iloc[0]
    dfflight["L"][dfflight["Altitude"] <= 1000] = npd_data_filt["L_1000ft"].iloc[0]
    dfflight["L"][dfflight["Altitude"] <= 630] = npd_data_filt["L_630ft"].iloc[0]
    dfflight["L"][dfflight["Altitude"] <= 400] = npd_data_filt["L_400ft"].iloc[0]
    dfflight["L"][dfflight["Altitude"] <= 200] = npd_data_filt["L_200ft"].iloc[0]
    # --------------------------------------------------
    # - Convert altitude to meters
    dfflight["Altitude(m)"] = dfflight["Altitude"]*0.3048

    #dfflight.to_csv("dataset.csv")
    return dfflight

# ------ Adds more data to the flight data by extrapolation
# ------ It works only for local coordinate system (not WGS)  (call after coordinate_objects())
def interpolate(dff):
    #dff["Altitude(m)"] = dff["Altitude"]*0.3048
    dfextr = pd.DataFrame(columns=dff.columns)
    for i in range(len(dff)-2):
        #dfextr.append(dff.iloc[i])
        x0 = dff["x"].iloc[i]
        y0 = dff['y'].iloc[i]
        z0 = dff['Altitude(m)'].iloc[i]
        current_time = dff["Timestamp"].iloc[i]
        time_dif = dff["Timestamp"].iloc[i+1] - current_time
        xend = dff["x"].iloc[i+1]
        yend = dff['y'].iloc[i+1]
        zend = dff['Altitude'].iloc[i+1]
        dt = 1 # seconds
        dfextr = pd.concat( [dfextr, dff[dff["Timestamp"] == current_time]])
        while(time_dif>2 ):
            dfextr = pd.concat( [dfextr, dff[dff["Timestamp"] == current_time]])
            last = len(dfextr)-1
            dt = 1
            x = x0 + dt*(xend-x0)/time_dif
            y = y0 + dt*(yend-y0)/time_dif
            z = z0 + dt*(zend-z0)/time_dif
            dfextr['x'].iloc[last] = x
            dfextr['y'].iloc[last] = y
            #dfextr['Altitude(m)'].iloc[last] = z
            dfextr['Timestamp'].iloc[last] = current_time + dt
            dt = dt + 1
            time_dif = time_dif-1
    dfextr = dfextr.reset_index(drop=True)
    #print("lenght of dfextr is ", len(dfextr), " and dff is ", len(dff))
    return dfextr
 
# -- Transforms coordinates into local coordinate system (do not send full data, only necessary parts - ON RUNWAY/ BEFORE/ [50]*AFTER)
def coordinate_objects(df, bool_interpolate):
    local_projection = 'epsg:32635'
    # Instantiate a Transformer
    transformer = Transformer.from_crs('epsg:4326', local_projection)
    df['x'], df['y'] = transformer.transform(df['LATITUDE'].values, df['LONGITUDE'].values)

    #dff = df[(df["RUN"] == "ON")| (df["RUN"] == "BEFORE")]
    #dff = df[(df["RUN"] == "ON")]
    #dff = df.iloc[47:100]
    if(bool_interpolate):
        dff = interpolate(df)
    else:
        dff = df
    
    #dff = df.iloc[47:70]
    latitude_values = dff['x'].values
    longitude_values = dff['y'].values

    latitude_values = dff['y'].values
    longitude_values = dff['x'].values
    l_values = dff['L'].values
    
    # Create the list of objects using zip and list comprehension
    objects = [(longitude, latitude, l) for latitude, longitude, l in zip(latitude_values, longitude_values, l_values)]
    return objects

def create_mesh():
    x_lat = 426870.9564985154 # calculated using Transformer
    y_lon = 4935609.810021779
    x = np.linspace(-10000 + x_lat, 10000 + x_lat, 1000)
    y = np.linspace(-10000 + y_lon, 10000 + y_lon, 1000)
    #X, Y = np.meshgrid(x, y)

    return x, y

def sound_dispersion(x, y, objects):
    X, Y = np.meshgrid(x, y)
    total_sound_level = 0
    for obj in objects:
        obj_pos = np.array([obj[0], obj[1]])
        obj_intensity = obj[2]
        obj_linear_intensity = 10**(obj_intensity/10)
        distance = np.sqrt((X - obj_pos[0])**2 + (Y - obj_pos[1])**2)
        sound_level_obj = obj_linear_intensity / (4*np.pi*distance**2)
        total_sound_level = total_sound_level + sound_level_obj
    total_sound_level_db = 10*np.log10(total_sound_level)

    return total_sound_level_db
