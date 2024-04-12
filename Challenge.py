
import json
import argparse
import csv
import sys
from xml.etree import ElementTree as ET

# Function to parse XML file
def parse_xml(file_path):
    data = []
    tree = ET.parse(file_path)
    root = tree.getroot()
    for ent in root.findall('.//ENT'):
        address = {
            'name': ent.findtext('NAME', default='').strip(),
            'organization': ent.findtext('COMPANY', default='').strip(),
            'street': ent.findtext('STREET', default='').strip(),
            'city': ent.findtext('CITY', default='').strip(),
            'county': '',
            'state': ent.findtext('STATE', default='').strip(),
            'zip': ent.findtext('POSTAL_CODE', default='').strip().split(' -')[0]
        }
        data.append(address)
    return data

# Function to parse TSV file
def parse_tsv(file_path):
    data = []
    with open(file_path, 'r') as file:
        tsv_reader = csv.DictReader(file, delimiter='\t')
        for row in tsv_reader:
            full_name = ' '.join(filter(None, [row['first'], row['middle'], row['last']])).strip()
            name_or_org = full_name if full_name else row['organization']
            address = {
                'name': name_or_org,
                'organization': row['organization'] if full_name else '',
                'street': row['address'],
                'city': row['city'],
                'county': row['county'],
                'state': row['state'],
                'zip': row['zip']
            }
            data.append(address)
    return data

# Function to parse TXT file
def parse_txt(file_path):
    data = []
    with open(file_path, 'r') as file:
        entry = {}
        for line in file:
            if line.strip() == '':  # Empty line signifies new entry
                if entry:  # If entry is not empty, append to data and reset for next entry
                    data.append(entry)
                    entry = {}
                continue
            if not entry.get('name'):  # The first non-empty line is the name
                entry['name'] = line.strip()
            elif not entry.get('street'):  # The second non-empty line is the street
                entry['street'] = line.strip()
            elif 'COUNTY' in line:  # Optional county line
                entry['county'] = line.strip().replace('COUNTY', '').strip()
            else:  # Next non-empty line should have city, state, zip
                parts = line.strip().split(', ')
                entry['city'] = parts[0]
                state_zip = parts[1].split(' ')
                entry['state'] = state_zip[0]
                entry['zip'] = state_zip[1] if len(state_zip) > 1 else ''
        # Don't forget to add the last entry after the loop finishes
        if entry:
            data.append(entry)
    return data

# Main function to process files
def main(files):
    if not files:
        print("Error: Please provide at least one input file containing addresses.", file=sys.stderr)
        return
    
    addresses = []
    for file_path in files:
        if file_path.endswith('.xml'):
            addresses.extend(parse_xml(file_path))
        elif file_path.endswith('.tsv'):
            addresses.extend(parse_tsv(file_path))
        elif file_path.endswith('.txt'):
            addresses.extend(parse_txt(file_path))
        else:
            print(f"Error: Unsupported file format for {file_path}", file=sys.stderr)
            continue
    # Sort addresses by ZIP code
    sorted_addresses = sorted(addresses, key=lambda x: x['zip'])
    # Output the list of addresses
    print(json.dumps(sorted_addresses, indent=4))

if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Process some addresses.')
    parser.add_argument('files', metavar='F', type=str, nargs='*',
                        help='an input file containing addresses')
    args = parser.parse_args()
    main(args.files)

    # Example function calls (move them outside the if __name__ == "__main__": block)
    xml_data = parse_xml('/Users/abhinavreddy/Desktop/input1.xml')
    tsv_data = parse_tsv('/Users/abhinavreddy/Desktop/input2.tsv')
    txt_data = parse_txt('/Users/abhinavreddy/Desktop/input3.txt')
