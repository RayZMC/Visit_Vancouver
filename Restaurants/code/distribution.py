import pandas as pd
import geopandas as gpd
from pyproj import CRS
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as ctx
import libpysal as lps
import esda
from esda.moran import Moran, Moran_Local
from splot.esda import moran_scatterplot, lisa_cluster
import folium


proj4_string = (
    "+proj=lcc +lat_1=49 +lat_2=77 +lat_0=63.390675 +lon_0=-91.8666666666667 "
    "+x_0=6200000 +y_0=3000000 +ellps=GRS80 +datum=NAD83 +units=m +no_defs"
)


def get_census_tract_gdf(filename):
    census_tract_gdf = gpd.read_file(filename)
    census_tract_gdf.crs = CRS.from_proj4(proj4_string)
    census_tract_gdf['CTUID'] = census_tract_gdf['CTUID'].astype('float64')
    census_tract_gdf['area'] = census_tract_gdf['geometry'].area  * 0.000001  # save area in km^2
    return census_tract_gdf


def get_restaurant_gdf(filename):
    restaurants_df = pd.read_json(filename, lines=True)
    restaurants_df = restaurants_df[['lat', 'lon', 'name', 'brand']]
    restaurants_df['is_chain'] = restaurants_df.apply(lambda x: is_chain(x), axis=1) 
    restaurants_gdf = gpd.GeoDataFrame(restaurants_df, 
                                      geometry=gpd.points_from_xy(restaurants_df.lon, restaurants_df.lat), 
                                      crs="EPSG:4326")
    return restaurants_gdf


def is_chain(row):
    if pd.isna(row['brand']):
        return False
    return True


def bar_graph_top_10(data):
    sns.barplot(data=data[:20], x='CTUID', y='count', hue='is_chain')
    plt.xlabel('Census Tract ID')
    plt.ylabel('count')
    plt.title('Number of Chain and Non-chain Restaurants by Census Tract')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('../visuals/bargraph_top10.png')


def chi2_test(contingency):
    chi2, chi_p, _, _ = stats.chi2_contingency(contingency)
    print("Chi-square statistic:", chi2)
    print("p-value:", chi_p)


def plot_restaurants_in_regions(census_tract_gdf, joined_gdf, is_chain):
    census_tract_gdf = census_tract_gdf.to_crs(epsg=3857)
    joined_gdf = joined_gdf.to_crs(epsg=3857)
    _, ax = plt.subplots(figsize=(15, 6))

    census_tract_gdf.plot(ax=ax, color='orange', edgecolor='white', alpha=0.5)
    ax.axis('off')
    
    if is_chain:
        restaurant_type = 'Chain'
        ax.set_title(restaurant_type)
    else:
        restaurant_type = 'Non-Chain'
        ax.set_title(restaurant_type)
        
    joined_gdf[joined_gdf['is_chain'] == is_chain].plot(ax=ax, color='red', markersize=5)
    
    ctx.add_basemap(ax=ax, source=ctx.providers.OpenStreetMap.Mapnik)
    plt.tight_layout()
    plt.savefig('../visuals/census_tract_map_with_' + restaurant_type + '.png')


def plot_restaurants_heatmap(census_tract_gdf, joined_gdf, is_chain):
    # Convert crs for Folium compatibility
    census_tract_gdf = census_tract_gdf.to_crs(epsg=4326)
    joined_gdf = joined_gdf.to_crs(epsg=4326)

    center_lat = census_tract_gdf.centroid.y.mean()
    center_lon = census_tract_gdf.centroid.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    locations = joined_gdf[joined_gdf['is_chain'] == is_chain][['geometry']].to_crs(epsg=4326)
    locations = locations['geometry'].apply(lambda geom: [geom.y, geom.x]).tolist()

    heatmap = HeatMap(locations, radius=10, blur=5, gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'})
    heatmap.add_to(m)

    if is_chain:
        m.save('../visuals/chains_heatmap.html')
    else:
        m.save('../visuals/non_chains_heatmap.html')


def choropleth_of_chains(chains_gdf):
    chains_gdf = chains_gdf.to_crs(epsg=3857)
    _, ax = plt.subplots(figsize=(15,15))
    chains_gdf.plot(ax=ax,
            column='count_per_km2',
            legend=True,
            alpha=0.7,
            cmap='RdYlGn_r',
            scheme='quantiles')
    ax.axis('off')
    ax.set_title('Chain restaurant count per km^2', fontsize=22)
    ctx.add_basemap(ax,source=ctx.providers.OpenStreetMap.Mapnik)
    plt.savefig('../visuals/chains_choropleth.png')


def global_spatial_autocorrelation(chains_gdf):
    # Calculate spatial weights: define neighbours spatially
    weight = lps.weights.KNN.from_dataframe(chains_gdf, k=8)
    weight.transform = 'r'

    # Calculate spatial lag: quantify the neighbours/average out their values into a single value
    chains_gdf['count_per_km2_lag'] = lps.weights.lag_spatial(weight, chains_gdf['count_per_km2'])

    chains_gdf['count_per_km2_lag_diff'] = chains_gdf['count_per_km2'] - chains_gdf['count_per_km2_lag']
    # print(chains_gdf.sort_values(by='count_per_km2_lag_diff'))

    y = chains_gdf['count_per_km2'] 
    moran = Moran(y, weight)
    print("Moran's I:", moran.I)
    print("p-value:", moran.p_sim)

    moran_scatterplot(moran, aspect_equal=True)
    plt.savefig('../visuals/morans_global_scatter.png')


def local_spatial_autocorrelation(chains_gdf):
    weight = lps.weights.KNN.from_dataframe(chains_gdf, k=8)
    weight.transform = 'r'
    y = chains_gdf['count_per_km2'] 

    lisa = esda.moran.Moran_Local(y, weight)

    _, ax = plt.subplots(figsize=(15,15))
    moran_scatterplot(lisa, ax=ax, p=0.05)
    plt.text(1.95, 0.5, "HH", fontsize=25)
    plt.text(1.95, -1, "HL", fontsize=25)
    plt.text(-2, 1, "LH", fontsize=25)
    plt.text(-1, -1, "LL", fontsize=25)
    plt.savefig('../visuals/morans_lisa_scatter.png')

    chains_gdf = chains_gdf.to_crs(epsg=3857)
    _, ax = plt.subplots(figsize=(14,12))
    lisa_cluster(lisa, chains_gdf, p=0.05, ax=ax, alpha=0.75)
    ctx.add_basemap(ax,source=ctx.providers.OpenStreetMap.Mapnik)
    plt.savefig('../visuals/morans_lisa_cluster.png')



def main():
    census_tract_gdf = get_census_tract_gdf('../data/vancouver_census_tract.geojson')
    restaurants_gdf = get_restaurant_gdf('../data/all_restaurants.json.gz')
    # convert crs so we can join with census tract
    restaurants_gdf = restaurants_gdf.to_crs(census_tract_gdf.crs)
    
    joined_gdf = restaurants_gdf.sjoin(census_tract_gdf, how='inner', predicate='within')  # 108 census tracts do not contain any restaurants
    joined_gdf = joined_gdf.drop(columns=['index_right']).reset_index(drop=True)

    contingency = pd.crosstab(joined_gdf['CTUID'], joined_gdf['is_chain'])

    restaurants = contingency.stack().reset_index()
    restaurants.columns = ['CTUID', 'is_chain', 'count']
    restaurants['total_count'] = restaurants.groupby('CTUID')['count'].transform('sum')
    restaurants_sorted = restaurants.sort_values(by='total_count', ascending=False)

    bar_graph_top_10(restaurants_sorted)

    chi2_test(contingency)

    plot_restaurants_in_regions(census_tract_gdf, joined_gdf, True)
    plot_restaurants_in_regions(census_tract_gdf, joined_gdf, False)

    chains = restaurants_sorted[restaurants_sorted['is_chain'] == True]
    chains = chains.merge(census_tract_gdf, on='CTUID')
    chains_gdf = gpd.GeoDataFrame(chains, 
                              geometry='geometry', 
                              crs=census_tract_gdf.crs)
    chains_gdf = chains_gdf.to_crs(census_tract_gdf.crs)
    chains_gdf['count_per_km2'] = chains_gdf['count'] / chains_gdf['area']

    choropleth_of_chains(chains_gdf)

    global_spatial_autocorrelation(chains_gdf)
    local_spatial_autocorrelation(chains_gdf)

    

if __name__ == "__main__":
    main()
    