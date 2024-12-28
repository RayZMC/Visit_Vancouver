import os
import sys
import pandas as pd
import numpy as np
from GPSPhoto import gpsphoto
import folium
from folium.plugins import MarkerCluster
from collections import defaultdict

def read_listing_csv(filename):
    return pd.read_csv(filename)

def load_amenity_data(category_name):
    filename = f"../data/data_{category_name}.json.gz"
    return pd.read_json(filename, compression='gzip', lines=True)

# adapted from: https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula/21623206
def calculate_distance(lat1, lon1, lat2, lon2):
    p = np.pi / 180
    a = 0.5 - np.cos((lat2 - lat1) * p) / 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    return 12742 * np.arcsin(np.sqrt(a)) * 1000.0

def find_nearest_amenities(hotel_lat, hotel_lon, amenity_data, search_radius):
    nearby_amenities = amenity_data[calculate_distance(hotel_lat, hotel_lon, amenity_data['lat'], amenity_data['lon']) <= search_radius]
    return len(nearby_amenities)

def main(search_radius, category_name):
    listings = read_listing_csv('../data/cleaned_listings/part-00000-31ca9434-e3f9-40c2-b2db-444521ac9e19-c000.csv')
    amenity_data = load_amenity_data(category_name)

    hotel_counts = defaultdict(int)
    for index, row in listings.iterrows():
        hotel_lat = row['latitude']
        hotel_lon = row['longitude']
        count = find_nearest_amenities(hotel_lat, hotel_lon, amenity_data, search_radius)
        hotel_counts[row['name']] = count

    # Find the hotel/airbnb with the highest count
    max_count = max(hotel_counts.values())
    top_hotels = [hotel for hotel, count in hotel_counts.items() if count == max_count]

    # take the first one
    top_hotel_name = top_hotels[0]

    # Get the details of the hotel with most amenities
    top_hotel = listings[listings['name'] == top_hotel_name]
    top_lat, top_lon = top_hotel['latitude'].iloc[0], top_hotel['longitude'].iloc[0]

    m = folium.Map(location=[top_lat, top_lon], zoom_start=15)

    folium.Marker([top_lat, top_lon], popup=top_hotel_name, icon=folium.Icon(color='red')).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)
    for index, amenity in amenity_data.iterrows():
        folium.Marker([amenity['lat'], amenity['lon']], popup=amenity['name']).add_to(marker_cluster)

    map_file = f"../maps/map_{category_name}_hotels.html"
    m.save(map_file)
    print(f"\nFolium map generated: {map_file}")

if __name__ == "__main__":
    search_radius = float(sys.argv[1])
    category_name = sys.argv[2]
    main(search_radius, category_name)
    