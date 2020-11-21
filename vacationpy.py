# imports
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import requests
import gmaps
import os
import json
# Import API key
from api_keys import g_key
# Load CSV file generated from WeatherPy Folder
weather_df=pd.read_csv("weather_df.csv")
dropna_weather_data = weather_df.dropna()
del dropna_weather_data["Unnamed: 0"]
dropna_weather_data.head()
# Configure gmaps
gmaps.configure(api_key=g_key)

# Locations
locations = dropna_weather_data[["Latitude", "Longitude"]]

humidity = dropna_weather_data["Humidity (%)"].astype(float)

# Plot Heatmap
fig = gmaps.figure()

# Create heat layer
heat_layer = gmaps.heatmap_layer(locations, weights=humidity, 
                                 dissipating=False, max_intensity=100,
                                 point_radius=2)

# Add layer
fig.add_layer(heat_layer)

# Display figure
fig

# Filter vacation with zero cloudiness
vacation_no_cloud = dropna_weather_data[dropna_weather_data["Cloudiness (%)"] == 0]
# Filter vacation with max temp above 70 degrees F
vacation_above_70_degrees = vacation_no_cloud[vacation_no_cloud["Max Temp (F)"] > 70]
# Filter vacation with max temp below 80 degrees F
vacation_below_80_degrees = vacation_above_70_degrees[vacation_above_70_degrees["Max Temp (F)"] < 80]
# Filter vacation with wind speed below 10 mph
vacation_slow_wind = vacation_below_80_degrees[vacation_below_80_degrees["Wind Speed (mph)"] < 10]
# Filter vacation with humidity below 60 %
perfect_vacation = vacation_slow_wind[vacation_slow_wind["Humidity (%)"] < 60]
# Set Index
indexed_perfect_vacation = perfect_vacation.reset_index()
del indexed_perfect_vacation["index"]
indexed_perfect_vacation

vaca_locations = indexed_perfect_vacation[["Latitude", "Longitude"]]

vaca_humidity = indexed_perfect_vacation["Humidity (%)"].astype(float)

# Plot Heatmap
vaca_fig = gmaps.figure()

# Create heat layer
vaca_heat_layer = gmaps.heatmap_layer(vaca_locations, weights=vaca_humidity, 
                                 dissipating=False, max_intensity=50,
                                 point_radius=2.5)

# Add layer
vaca_fig.add_layer(vaca_heat_layer)

# Display figure
vaca_fig

# Hotel variable
hotels = []

# Loop through narrowed down dataframe to get nearest hotel
for city in range(len(indexed_perfect_vacation["City"])):

    lat = indexed_perfect_vacation.loc[city]["Latitude"]
    lng = indexed_perfect_vacation.loc[city]["Longitude"]

    city_coords = f"{lat},{lng}"

    params = {
        "location": city_coords, 
        "types": "lodging",
        "radius": 5000,
        "key": g_key
    }

    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"   

    hotel_request = requests.get(base_url, params=params)
    hotel_response = hotel_request.json()

    try:
        hotels.append(hotel_response["results"][0]["name"])
    except:
        hotels.append("Nearest hotel not found")

# Dataframe with nearest hotel
indexed_perfect_vacation["Nearest Hotel"] = hotels
indexed_perfect_vacation

# Using the template add the hotel marks to the heatmap
info_box_template = """
<dl>
<dt>Name</dt><dd>{Nearest Hotel}</dd>
<dt>City</dt><dd>{City}</dd>
<dt>Country</dt><dd>{Country}</dd>
</dl>
"""
# Store the DataFrame Row
# NOTE: be sure to update with your DataFrame name
hotel_info = [info_box_template.format(**row) for index, row in indexed_perfect_vacation.iterrows()]
locations = indexed_perfect_vacation[["Latitude", "Longitude"]]

# Add marker layer ontop of heat map
markers = gmaps.marker_layer(locations, info_box_content= [f"Nearest Hotel: {hotel}" for hotel in hotels])
vaca_fig.add_layer(markers)

# Display Map
vaca_fig