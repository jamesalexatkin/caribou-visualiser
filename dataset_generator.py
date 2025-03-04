import argparse
import os

import geocoder
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from _datetime import date
import json
import us
import random
import re


def read_api_key(filename):
    api_key = ""
    with open(filename, 'r') as f:        
        api_key = f.read()
    return api_key

def format_html_number(num_str):
    result = ""
    for char in num_str:
        if char.isdigit():
            result = result + char
    return int(result)

def convert_to_base_state_link(state_link):
    regex = "(us/[a-z]{2}).*"

    search = re.search(regex, state_link, re.IGNORECASE)

    if search:
        return search.group(1)
    else:
        return ""

def rchop(s, suffix):
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    return s

def find_county_of_city(city_name, state_name):
    search_string = city_name + ", " + state_name
    # print(search_string)
    results = geocoder.google(search_string, key=GOOGLE_MAPS_API_KEY)

    returned_county = results.current_result.county

    if returned_county:
        return rchop(returned_county, " County")
    else:
        return city_name

def format_county(county_of_city, state_name, geo_id):
    formatted_county = county_of_city + ", " + state_name + ", " + geo_id
    return formatted_county

def find_geo_id(county, state, counties_json):
    fips = us.states.lookup(state).fips

    for prospective_county in counties_json["features"]:
        prospective_county_properties = prospective_county["properties"]
        if prospective_county_properties["NAME"] == county and prospective_county_properties["STATE"] == fips:
            return prospective_county_properties["GEO_ID"]

    return ""

def get_state_id(state_name):
    return us.states.lookup(state_name).abbr

def add_count_to_states(state_counts, num_in_state, state_id):
    if state_id in state_counts and state_counts[state_id] != "":
        state_counts[state_id] = state_counts[state_id] + num_in_state
    else:
        state_counts[state_id] = num_in_state

def write_states_csv(state_counts, output_path):
    with open(output_path, 'w+') as f:
        f.write("%s,%s\n" % ("id", "Number"))
        for key in state_counts.keys():
            f.write("%s,%s\n" % (key, state_counts[key]))

def add_count_to_counties(county_counts, num_in_city, geo_id):
    if geo_id in county_counts and county_counts[geo_id] != "":
        county_counts[geo_id] = county_counts[geo_id] + num_in_city
    else:
        county_counts[geo_id] = num_in_city

def write_counties_csv(county_counts, output_path):
    with open(output_path, 'w+') as f:
        f.write("%s,%s\n" % ("GEO_ID", "Number"))
        for key in county_counts.keys():
            f.write("%s,%s\n" % (key, county_counts[key]))


##### MAIN #####

# Set up arg parser
parser = argparse.ArgumentParser()
parser.add_argument("api_key_path", help="Path to file containing API key for Google Maps API")
parser.add_argument("region_type", choices=['states', 'counties'], help="Whether to produce a map of states or counties")

# Parse args
args = parser.parse_args()
api_key_path = args.api_key_path
region_type = args.region_type

# Read API key from file
GOOGLE_MAPS_API_KEY = read_api_key(api_key_path)

CARIBOU_BASE_URL = "https://locations.cariboucoffee.com/"
CARIBOU_LOCATIONS_URL = os.path.join(CARIBOU_BASE_URL, "us")

page = requests.get(CARIBOU_LOCATIONS_URL)

soup = BeautifulSoup(page.content, 'html.parser')

html_results = soup.find(id='main')

list_items = html_results.find_all('li', class_='Directory-listItem')


# Sample map at state-level
if region_type == "states":
    
    state_counts = {}

    STATES_FILE = os.path.join("datasets", "us_states.json")
    states_json = json.load(open(STATES_FILE))

    for s in states_json["features"]:
        state_id = s["id"]
        add_count_to_states(state_counts, "", state_id)

    for li in tqdm(list_items):
        list_link = li.find('a')

        state_name = list_link.text
        state_link = list_link['href']

        # Extract number of stores in state from HTML to an int
        num_in_state = format_html_number(li.find('span').text)

        state_id = get_state_id(state_name)

        add_count_to_states(state_counts, num_in_state, state_id)


    output_filename = "caribou_" + region_type + "_dataset_" + date.today().strftime("%d-%m-%y") + ".csv"
    output_path = os.path.join('./datasets/', output_filename)
    write_states_csv(state_counts, output_path)

# Sample map at county-level
elif region_type == "counties":

    county_counts = {}

    COUNTIES_FILE = os.path.join("datasets", "us_counties_500k.json")
    counties_json = json.load(open(COUNTIES_FILE))

    for c in counties_json["features"]:
        geo_id = c["properties"]["GEO_ID"]
        add_count_to_counties(county_counts, "", geo_id)

    for li in tqdm(list_items):
        list_link = li.find('a')

        state_name = list_link.text
        state_link = list_link['href']

        # Extract number of stores in state from HTML to an int
        num_in_state = format_html_number(li.find('span').text)

        # Edge case where states only have one store
        # Caribou website has the link directly to the store, rather than the state
        if num_in_state == 1:
            state_link = convert_to_base_state_link(state_link)


        state_page_url = os.path.join(CARIBOU_BASE_URL, state_link)
        state_page = requests.get(state_page_url)
        state_soup = BeautifulSoup(state_page.content, 'html.parser')
        state_html_results = state_soup.find(id='main')

        city_list_items = state_html_results.find_all('li', class_='Directory-listItem')

        for city_li in city_list_items:
            city_list_link = city_li.find('a')

            city_name = city_list_link.text     

            # Extract number of stores in city from HTML to an int
            num_in_city = format_html_number(city_li.find('span').text)

            county_of_city = find_county_of_city(city_name, state_name)

            geo_id = find_geo_id(county_of_city, state_name, counties_json)
            
            add_count_to_counties(county_counts, num_in_city, geo_id)

    output_filename = "caribou_" + region_type + "_dataset_" + date.today().strftime("%d-%m-%y") + ".csv"
    output_path = os.path.join('./datasets/', output_filename)
    write_counties_csv(county_counts, output_path)