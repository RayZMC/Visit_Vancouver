import pandas as pd

def save_category_data(category_data):
    if not category_data.empty:
        category_name = category_data['category'].iloc[0]
        category_data.to_json(f'../data/data_{category_name}.json.gz', orient='records', lines=True, compression='gzip')

def main():
    filename = '../data/amenities-vancouver.json.gz'
    data = pd.read_json(filename, lines=True, orient='records', compression='gzip')
    data['amenity'] = data['amenity'].astype('string')
    
    # Categories of amenities
    categories = {
        'tourism': ['Observation Platform', 'cinema', 'clock', 'arts_centre', 'park', 'townhall'],
        'food': ['restaurant', 'cafe', 'bbq', 'food_court', 'ice_cream', 'vending_machine', 'bistro', 'fast_food', 'bar'],
        'transportation': ['bicycle_rental',  'bus_station',  'ferry_terminal',  'taxi'],
        'entertainment': ['spa', 'casino', 'leisure', 'nightclub', 'theatre', 'playground', 'pub', 'gym', 'social_centre', 'gambling', 'exhibition_centre', 'events_venue', 'community_centre', 'conference_centre', 'music_venue', 'planetarium'],
        'schools': ['university', 'college', 'school', 'library',  'research_institute']
    }


    data['category'] = None
    for category, amenity_types in categories.items():
        data.loc[data['amenity'].isin(amenity_types), 'category'] = category
    
    data.groupby('category').apply(save_category_data)

if __name__ == '__main__':
    main()