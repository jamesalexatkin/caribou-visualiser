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

def add_count_to_counties(county_counts, num_in_city, geo_id):
    if geo_id in county_counts and county_counts[geo_id] != "":
        county_counts[geo_id] = county_counts[geo_id] + num_in_city
    else:
        county_counts[geo_id] = num_in_city

def write_csv(county_counts):
    csv_filename = "caribou_dataset_{0}.csv".format(date.today().strftime("%d-%m-%y"))
    csv_path = os.path.join("datasets", csv_filename)

    with open(csv_path, 'w+') as f:
        f.write("%s,%s\n" % ("GEO_ID", "Number"))
        for key in county_counts.keys():
            f.write("%s,%s\n" % (key, county_counts[key]))


##### MAIN #####

# Set up arg parser
parser = argparse.ArgumentParser()
parser.add_argument("api_key_path", help="Path to file containing API key for Google Maps API")

# Parse args
args = parser.parse_args()

# Read API key from file
GOOGLE_MAPS_API_KEY = read_api_key(args.api_key_path)


CARIBOU_BASE_URL = "https://locations.cariboucoffee.com/"
CARIBOU_LOCATIONS_URL = os.path.join(CARIBOU_BASE_URL, "us")

page = requests.get(CARIBOU_LOCATIONS_URL)

soup = BeautifulSoup(page.content, 'html.parser')

html_results = soup.find(id='main')

list_items = html_results.find_all('li', class_='Directory-listItem')

county_counts = {}

COUNTIES_FILE = os.path.join("datasets", "us_counties_500k.json")
counties_json = json.load(open(COUNTIES_FILE))

for c in counties_json["features"]:
    geo_id = c["properties"]["GEO_ID"]
    # r = random.randint(0, 10)
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

write_csv(county_counts)