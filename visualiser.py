# Import libraries
import pandas as pd
import folium
import os
from datetime import date
 
# Load the shape of the zone (US states)
# Find the original file here: https://github.com/python-visualization/folium/tree/master/examples/data
# You have to download this file and set the directory where you saved it
state_geo = os.path.join('./', 'us-states.json')
 
# Load the unemployment value of each state
# Find the original file here: https://github.com/python-visualization/folium/tree/master/examples/data
num_stores = os.path.join('./', 'US_Caribou_Coffee_Stores_May2020.csv')
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