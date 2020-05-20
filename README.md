<h1 align="center" padding="100">Caribou Coffee Stores by County</h1>
<p align="center">Choropleth visualisation of Caribou coffee stores in the US.</p>

## 🙋 What is this?

This project allows for the visualisation of the number of Caribou Coffee stores in the United States by state counties. The resulting visualisation is in the form of a [choropleth](https://en.wikipedia.org/wiki/Choropleth_map), or shaded map. Darker regions represent a higher number of coffee stores.

## 🏃‍♀️ Running the code

I have included code both to generate a dataset and visualise a dataset.

### 📊 Generating a dataset

Dataset generation is performed by scraping the Caribou website to find store locations and matching these up with US counties. Counties are searched using the Google Maps API and a valid key must be provided. The path to a file containing only the API key as string should be passed to the script as an argument.

The script can be run as follows:

`python dataset_generator.py <FILE CONTAINING API KEY>`

The dataset produced is output as a CSV file.

### ✒️ Visualisation

If you wish to use a readymade dataset, one can be found in the `datasets` folder, or else you can follow the previous steps to create your own.

The Caribou dataset must be passed to the visualiser script as an argument.

The script can be run as follows:

`python visualiser.py <CARIBOU DATASET>`

## 💻 Technology

This project was written in Python 3.8.0 and tested on Windows 10 Home.

## 🙏 Acknowledgements

The dataset of US counties used is provided under `datasets` courtesy of [Eric Celeste](https://eric.clst.org/tech/usgeojson/).