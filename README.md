# Visit Vancouver
Exploring a new city is an adventure filled with endless possibilities waiting to be
discovered around every corner. However, sometimes it is easy to miss certain points of interest if
you do not plan ahead. Planning a tour of a city means finding exciting places to visit, such as
landmarks, entertainment, and food. It's also helpful to know where chain restaurants are compared
to local ones, to see the city's food scene. Furthermore, when choosing a place to stay, it's important
to pick somewhere close to fun things to do. This project will aim to enhance the city exploration
experience by offering information on must-see attractions, navigating diverse culinary landscapes,
and selecting convenient accommodations near key amenities and attractions. Specifically, the
project aims to solve the following questions:

1. What routes in the city offer a variety of interesting locations?
2. Are chain restaurants more common in certain areas, and how can their density be visualized?
3. Which Airbnb locations have the best nearby amenities?

## Set up
Install libraries:
```
pip install pandas numpy folium geopandas pyproj seaborn contextily libpysal esda gpsphoto pyspark exifread splot scipy matplotlib
```

## Run the Project
#### Tour of the City:
```
cd ./CMPT-353-Final-Project/Tour/code/
```
```
python3 find_amenity.py photos_directory search_radius amenity_category
```
Example: python3 find_amenity.py downtown_walk 200 food

Note 1: amenity_category must be one of tourism, food, transportation, entertainment, schools

Note 2: "photos_directory" must be the name of a folder containing geotagged images. A sample folder "downtown_walk" has been provided inside CMPT-353-Final-Project/Tour/code/

#### Find Airbnb:
```
cd ./CMPT-353-Final-Project/Tour/code/
```
```
python3 find_airbnb.py search_radius amenity_category
```
Example: python3 find_airbnb.py 50 food

Note: amenity_category must be one of tourism, food, transportation, entertainment, schools

#### Chain Restaurants:
```
cd ./CMPT-353-Final-Project/Restaurants/code/
```
```
python3 distribution.py
```

## Expected Output
#### Tour of the City:
Upon successful execution, the program will output: 

Maps to ./CMPT-353-Final-Project/Tour/maps/
- map_category_downtown_walk.html (Example: "python3 find_amenity.py downtown_walk 200 food" will output "map_food_downtown_walk.html")

#### Find Airbnb:
Upon successful execution, the program will output: 

Maps to ./CMPT-353-Final-Project/Tour/maps/
- map_category_hotels.html (Example: "python3 find_airbnb.py 50 food" will output "map_food_hotels.html")

#### Chain Restaurants:
Upon successful execution, the program will output: 

Plots to ./CMPT-353-Final-Project/Restaurants/visual/
- bargraph_top10.png
- census_tract_map_with_Chain.png
- census_tract_map_with_Non-Chain.png
- chains_choropleth.png
- morans_global_scatter.png
- morans_lisa_cluster.png
- morans_lisa_scatter.png

To the terminal
- Chi-square statistic and corresponding p-value
- Moran's I value and corresponding p-value
