import xml.etree.ElementTree as ET
import json
import gzip


def parse_xml_to_json(input_filename, output_filename):
    # Parse XML
    tree = ET.parse(input_filename)
    root = tree.getroot()

    # Open output file to write JSON
    with gzip.open(output_filename, 'wt') as f:
        # Iterate over each node in the XML and extract information
        for node in root.findall('node'):
            node_data = {
                "lat": float(node.attrib.get('lat')),
                "lon": float(node.attrib.get('lon')),
                "timestamp": "",
                "amenity": "",
                "name": ""
            }
            
            # Extract other tags as separate fields
            for tag in node.findall('tag'):
                key = tag.attrib.get('k')
                value = tag.attrib.get('v')
                node_data[key] = value
            
            # Write node data as a JSON object to output file
            f.write(json.dumps(node_data) + '\n')

if __name__ == "__main__":
    parse_xml_to_json('../data/all_restaurants.osm', '../data/all_restaurants.json.gz')
    