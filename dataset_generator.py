import argparse

import geocoder


def read_api_key(filename):
    api_key = ""
    with open(filename, 'r') as f:        
        api_key = f.read()
    return api_key


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

CARIBOU_WEB_ADDRESS = "https://locations.cariboucoffee.com/us"







results = geocoder.google("Albert Lea, Minnesota", key=GOOGLE_MAPS_API_KEY)

print(results.current_result.county)
