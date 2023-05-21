import pandas as pd
from pyproj import Transformer
def lrop_data():
    datadict = {"APT_ID":["LROP"], "REF_POINT_LAT":[44.5711], "REF_POINT_LONG":[26.0850],
                "RUN1_LAT_START":[44.576622], "RUN1_LONG_START":[26.0841], "RUN1_LAT_END":[44.579925], "RUN1_LONG_END":[26.127764],
                "RUN2_LAT_START":[44.564661], "RUN2_LONG_START":[26.076747], "RUN2_LAT_END":[44.567969], "RUN2_LONG_END":[26.120428], "ELEVATION" :[313]}
    datalrop = pd.DataFrame(data=datadict)

    # -- Transform coordinates to local system (meters)
    local_projection = 'epsg:32635'

    # Instantiate a Transformer
    transformer = Transformer.from_crs('epsg:4326', local_projection)

    datalrop['RUN1_LAT_START_tr'], datalrop["RUN1_LONG_START_tr"] = transformer.transform(datalrop['RUN1_LAT_START'].values, datalrop["RUN1_LONG_START"].values)
    datalrop["RUN1_LAT_END_tr"], datalrop["RUN1_LONG_END_tr"] = transformer.transform(datalrop["RUN1_LAT_END"].values, datalrop["RUN1_LONG_END"].values)

    datalrop['RUN2_LAT_START_tr'], datalrop["RUN2_LONG_START_tr"] = transformer.transform(datalrop['RUN2_LAT_START'].values, datalrop["RUN2_LONG_START"].values)
    datalrop["RUN2_LAT_END_tr"], datalrop["RUN2_LONG_END_tr"] = transformer.transform(datalrop["RUN2_LAT_END"].values, datalrop["RUN2_LONG_END"].values)

    return datalrop