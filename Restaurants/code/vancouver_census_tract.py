import geopandas as gpd

census_tract = gpd.read_file('../data/census_tract/census_tract.shp')
vancouver = census_tract[census_tract['CMANAME'] == "Vancouver"]
vancouver_gdf = gpd.GeoDataFrame(vancouver[['CTUID', 'geometry']],
                                 geometry='geometry')
vancouver_gdf.to_file('../data/vancouver_census_tract.geojson', driver='GeoJSON')
