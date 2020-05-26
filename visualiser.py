# Import libraries
import argparse
import json
import os
from datetime import date

import folium
import pandas as pd

# Set up arg parser
parser = argparse.ArgumentParser()
parser.add_argument("caribou_dataset_path", help="Path to CSV dataset for number of Caribou dataset")
parser.add_argument("region_type", choices=['states', 'counties'], help="Whether to produce a map of states or counties")

# Parse args
args = parser.parse_args()
num_stores = args.caribou_dataset_path
region_type = args.region_type

# Load the Caribou dataset
county_data = pd.read_csv(num_stores)

# Initialize the map:
m = folium.Map(location=[38, -103], zoom_start=5)

# Map at state-level
if region_type == "states":
    # Load the shape of US states
    states_geo_filename = os.path.join('./datasets', 'us_states.json')

    folium.Choropleth(
        geo_data=states_geo_filename,
        data=county_data,
        columns=['id','Number'],
        key_on='feature.id',
        fill_color='YlGnBu',
        fill_opacity=0.8,
        line_weight=1,
        legend_name='Number of Caribou Coffee Stores'
    ).add_to(m)

# Map at county-level
elif region_type == "counties":
    # Load the shape of US counties
    county_geo_filename = os.path.join('./datasets', 'us_counties_500k.json') # from http://eric.clst.org/Stuff/USGeoJSON

    folium.Choropleth(
        geo_data=county_geo_filename,
        data=county_data,
        columns=['GEO_ID','Number'],
        key_on='properties.GEO_ID',
        fill_color='YlGnBu',
        fill_opacity=0.8,
        line_weight=1,
        legend_name='Number of Caribou Coffee Stores'
    ).add_to(m)
 
# Save to html file
output_filename = "caribou_" + region_type + "_map_" + date.today().strftime("%d-%m-%y") + ".html"
output_path = os.path.join('./results/', output_filename)
m.save(output_path)