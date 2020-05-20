import argparse

import geocoder
import requests

from bs4 import BeautifulSoup
import os


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
    print(search_string)
    results = geocoder.google(search_string, key=GOOGLE_MAPS_API_KEY)

    if results:
        return results.current_result.county
    else:
        # TODO: error handling
        return ""

##### MAIN #####

# Set up arg parser
parser = argparse.ArgumentParser()
parser.add_argument("api_key_path", help="Path to file containing API key for Google Maps API")

# Parse args
args = parser.parse_args()

# Read API key from file
GOOGLE_MAPS_API_KEY = read_api_key(args.api_key_path)


# TODO: steps
# go to webpage
# get page element of list
# for each item
# get state name
# go to state page
# get page element of list
# for each item
# get city name
# look up county
# get number in city
# add to county

# write whole thing to csv

CARIBOU_BASE_URL = "https://locations.cariboucoffee.com/"
CARIBOU_LOCATIONS_URL = os.path.join(CARIBOU_BASE_URL, "us")

page = requests.get(CARIBOU_LOCATIONS_URL)

soup = BeautifulSoup(page.content, 'html.parser')

html_results = soup.find(id='main')

list_items = html_results.find_all('li', class_='Directory-listItem')

for li in list_items:
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

            


# results = geocoder.google("Albert Lea, Minnesota", key=GOOGLE_MAPS_API_KEY)

# print(results.current_result.county)
