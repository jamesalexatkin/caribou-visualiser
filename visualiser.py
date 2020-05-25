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

# Parse args
args = parser.parse_args()

# Load the shape of US counties
county_geo_filename = os.path.join('./datasets', 'us_counties_500k.json') # from http://eric.clst.org/Stuff/USGeoJSON

# Load the Caribou dataset
num_stores = args.caribou_dataset_path
county_data = pd.read_csv(num_stores)

# Initialize the map:
m = folium.Map(location=[37, -102], zoom_start=4)

folium.Choropleth(
    geo_data=county_geo_filename,
    data=county_data,
    # columns=['County', ' Number'],
    columns=['GEO_ID','Number'],
    key_on='properties.GEO_ID',
    fill_color='YlGnBu',
    fill_opacity=0.8,
    line_weight=1,
    legend_name='Number of Caribou Coffee Stores'
).add_to(m)
 
# Save to html file
output_filename = "caribou_map_" + date.today().strftime("%d-%m-%y") + ".html"
m.save(output_filename)