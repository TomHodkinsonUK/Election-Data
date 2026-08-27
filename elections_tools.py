import csv
import requests #type: ignore

# MAIN PROGRAM
def main():
    choice = input("Would you like to (1) create a CSV or (2) compare elections? ")

    if choice == "1":
        classification = input("Select classification (counties/districts): ").strip().lower()
        url = input("URL: ")
        data = download_data(url)
        filename = input("Filename: ")
        create_csv(data, filename, classification)

    elif choice == "2":
        classification = input("Select classification (counties/districts): ").strip().lower()
        first_file = input("First CSV file: ")
        second_file = input("Second CSV file: ")
        year_1 = int(input("First election year: "))
        year_2 = int(input("Second election year: "))
        filename = input("Comparison CSV filename: ")
        compare_data(first_file, second_file, filename, year_1, year_2, classification)

def download_data(url):
    response = requests.get(url)
    data = response.json()
    return data

def create_csv(data, filename, classification):
    region_label = "county" if classification == "counties" else "district"

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'state',
            region_label,
            'geoid',
            'total_votes',
            'party',
            'votes',
            'percentage'
        ])

        # Richmond-compatible JSON uses "counties"
        # even when the records represent congressional districts.
        region_list = data.get('coutnies', [])

        for region in region_list:
            state = region.get('a')
            name = region.get('n')
            geoid = region.get('j')
            total_votes = region.get('tv')

            for party in region.get('v', []):
                party_name = party.get('p')
                votes = party.get('v')
                raw_perc = party.get('perc')
                percentage = raw_perc * 100 if raw_perc is not None else "N/A"

                writer.writerow([
                    state,
                    name,
                    geoid,
                    total_votes,
                    party_name,
                    votes,
                    percentage
                ])
def compare_data(first_file, second_file, filename, year_1, year_2, classification):
    region_label = "county" if classification == "counties" else "district"

    with open(first_file, newline='') as file:
        reader = csv.DictReader(file)
        first_data = list(reader)

    with open(second_file, newline='') as file:
        reader = csv.DictReader(file)
        second_data = list(reader)

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['year_1', 'year_2', 'state', region_label, 'geoid', 'party', 'percentage_year_1', 'percentage_year_2', 'percentage_point_change'])

        all_combinations = set()

        for row in first_data:
            all_combinations.add((row['geoid'], row['party']))

        for row in second_data:
            all_combinations.add((row['geoid'], row['party']))

        for geoid, party in all_combinations:
            row_1 = next((r for r in first_data if r['geoid'] == geoid and r['party'] == party), None)
            row_2 = next((r for r in second_data if r['geoid'] == geoid and r['party'] == party), None)

            if row_1 is not None:
                state = row_1['state']
                region_name = row_1.get(region_label, row_1.get('county', row_1.get('district', '')))
            else:
                state = row_2['state']
                region_name = row_2.get(region_label, row_2.get('county', row_2.get('district', '')))

            try:
                percentage_1 = float(row_1['percentage']) if row_1 and row_1['percentage'] != "N/A" else "N/A"
            except (ValueError, TypeError):
                percentage_1 = "N/A"

            try:
                percentage_2 = float(row_2['percentage']) if row_2 and row_2['percentage'] != "N/A" else "N/A"
            except (ValueError, TypeError):
                percentage_2 = "N/A"

            if isinstance(percentage_1, (int, float)) and isinstance(percentage_2, (int, float)):
                percentage_point_change = percentage_2 - percentage_1
            else:
                percentage_point_change = "N/A"

            writer.writerow([year_1, year_2, state, region_name, geoid, party, percentage_1, percentage_2, percentage_point_change])

if __name__ == '__main__':
    main()
