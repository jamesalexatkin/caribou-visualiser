import argparse
import os

import geocoder
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from _datetime import date


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

def find_county_of_city(city_name, state_name):
    search_string = city_name + ", " + state_name
    # print(search_string)
    results = geocoder.google(search_string, key=GOOGLE_MAPS_API_KEY)

    if results.current_result.county:
        return results.current_result.county
    else:
        return search_string

def format_county(county_of_city, state_name):
    formatted_county = county_of_city + ", " + state_name
    return formatted_county

def add_count_to_counties(county_counts, num_in_city, formatted_county):
    if formatted_county in county_counts:
        county_counts[formatted_county] = county_counts[formatted_county] + num_in_city
    else:
        county_counts[formatted_county] = num_in_city

def write_csv(county_counts):
    csv_filename = "caribou_dataset_{0}.csv".format(date.today().strftime("%m-%d-%y"))
    csv_path = os.path.join("datasets", csv_filename)

    with open(csv_path, 'w+') as f:
        f.write("%s, %s, %s\n" % ("County", "State", "Number"))
        for key in county_counts.keys():
            f.write("%s, %s\n" % (key, county_counts[key]))


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

for li in tqdm(list_items):
    list_link = li.find('a')

    state_name = list_link.text
    state_link = list_link['href']

    # Extract number of stores in state from HTML to an int
    num_in_state = format_html_number(li.find('span').text)

    if num_in_state == 1:
        # TODO: handle case where state only has one store
        pass
    # Else state has multiple stores
    else:
        state_page_url = os.path.join(CARIBOU_BASE_URL, state_link)
        state_page = requests.get(state_page_url)
        state_soup = BeautifulSoup(state_page.content, 'html.parser')
        state_html_results = state_soup.find(id='main')

        city_list_items = state_html_results.find_all('li', class_='Directory-listItem')

        for city_li in city_list_items:
            city_list_link = city_li.find('a')

            city_name = city_list_link.text     

            # Extract number of stores in city from HTML to an int
            num_in_city = format_html_number(li.find('span').text)

            county_of_city = find_county_of_city(city_name, state_name)

            formatted_county = format_county(county_of_city, state_name)
            
            add_count_to_counties(county_counts, num_in_city, formatted_county)

write_csv(county_counts)