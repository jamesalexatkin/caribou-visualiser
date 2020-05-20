# Import libraries
import argparse
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
state_geo = os.path.join('./datasets', 'us-states.json')
 
# Load the number of stores for each county
num_stores = args.caribou_dataset_path
state_data = pd.read_csv(num_stores)
 
# Initialize the map:
m = folium.Map(location=[37, -102], zoom_start=5)
 
# Add the color for the chloropleth:
m.choropleth(
 geo_data=state_geo,
 name='choropleth',
 data=state_data,
 columns=['State', 'Stores'],
 key_on='feature.id',
 fill_color='GnBu',
 fill_opacity=0.7,
 line_opacity=0.2,
 legend_name='Number of Caribou Coffee Stores'
)
folium.LayerControl().add_to(m)
 
# Save to html file
output_filename = "caribou_map_" + date.today().strftime("%m/%d/%y")
m.save(output_filename)
