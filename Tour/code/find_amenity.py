import os
import sys
import pandas as pd
import numpy as np
from PIL import Image
from GPSPhoto import gpsphoto
import folium

def load_dataset(amenity_type):
    filename = f"../data/data_{amenity_type}.json.gz"
    return pd.read_json(filename, compression='gzip', lines=True)

def preprocess_dataset(dataset, coordinates):
    dataset['pic_lat'] = coordinates[0]
    dataset['pic_lon'] = coordinates[1]
    return dataset.dropna(subset=['name'])

# adapted from: https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula/21623206
def distance_formula(row):
    lat1 = row['pic_lat']
    lon1 = row['pic_lon']
    lat2 = row['lat']
    lon2 = row['lon']
    p = np.pi / 180
    a = 0.5 - np.cos((lat2 - lat1) * p) / 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    return 12742 * np.arcsin(np.sqrt(a)) * 1000.0  

def filter_by_radius_and_amenity(dataset, search_radius):
    dataset['distance'] = dataset.apply(distance_formula, axis=1)
    return dataset[dataset['distance'] <= search_radius].sort_values(by='distance')

def save_results(dataset, output_path):
    dataset[['amenity', 'name', 'distance']].to_json(output_path, orient='records', lines=True)

# adapted from: https://stackoverflow.com/questions/19804768/interpreting-gps-info-of-exif-data-from-photo-in-python
def readImageGPS(filename):
    try:
        data = gpsphoto.getGPSData(filename)
        lat = data.get('Latitude')
        lon = data.get('Longitude')
        if lat is not None and lon is not None:
            return lat, lon
        else:
            raise ValueError("Latitude or Longitude data not found in the image. Image may not be geotagged.")
    except Exception as e:
        print(f"Error reading GPS data from {filename}: {e}")
        return None, None


def main(image_path, search_radius, amenity_type, m=None, filename=None):
    # Get GPS coordinates from the image
    coordinates = readImageGPS(image_path)
    print(f"\nGPS coordinates read from {filename}: {coordinates}")

    # Load and preprocess dataset
    dataset = load_dataset(amenity_type)
    dataset = preprocess_dataset(dataset, coordinates)

    # Filter out places based on the search radius
    filtered_dataset = filter_by_radius_and_amenity(dataset, search_radius)
    
    # Print and save results
    #print(f"\n{amenity_type.capitalize()}s within a {search_radius} meter radius for {filename}:")
    #print(filtered_dataset[['amenity', 'name', 'distance']])

    # Create a Folium map
    if m is None:
        m = folium.Map(location=coordinates, zoom_start=15)

    # Marker for image location
    icon_image = 'stickman_walk.png'
    icon = folium.CustomIcon(icon_image, icon_size=(30, 30))
    folium.Marker(location=coordinates, icon=icon).add_to(m)
    
    # Add markers for each amenity
    for index, row in filtered_dataset.iterrows():
        popup_text = f"{row['name']} ({row['amenity'].capitalize()}) - Distance: {row['distance']:.2f} meters"
        folium.Marker([row['lat'], row['lon']], popup=popup_text).add_to(m)

    return m

if __name__ == '__main__':
    photos_directory = sys.argv[1]
    search_radius = float(sys.argv[2])
    amenity_type = sys.argv[3]

    m = None  # Initialize the map outside the loop
    # Iterate over each photo in the directory
    for filename in os.listdir(photos_directory):
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            image_path = os.path.join(photos_directory, filename)
            m = main(image_path, search_radius, amenity_type, m, filename=filename)

    # Save the map as an HTML file
    map_file = f"../maps/map_{amenity_type}_{photos_directory}.html"
    m.save(map_file)
    print(f"\nFolium map generated: {map_file}")
