import pandas as pd 

def apply_corrections(data, corrections_file, year):

    corrections = pd.read_csv(corrections_file)

    # Only apply corrections for the election year
    corrections = corrections[
        corrections['year'] == year
    ]

    # Apply each verified correction
    for _, correction in corrections.iterrows():

        state = correction['state']
        county = correction['county']
        party = correction['party']
        correct_votes = correction['correct_votes']

        # Find the existing row
        mask = (
            (data['state'] == state) &
            (data['county'] == county) &
            (data['party'] == party)
        )

        if mask.any():

            # Correct an existing candidate
            data.loc[mask, 'votes'] = correct_votes

        else:

            # Candidate is missing from the original data
            county_mask = (
                (data['state'] == state) &
                (data['county'] == county)
            )

            if county_mask.any():

                # Get the county's existing information
                total_votes = data.loc[
                    county_mask,
                    'total_votes'
                ].iloc[0]

                geoid = data.loc[
                    county_mask,
                    'geoid'
                ].iloc[0]

                # Create the missing candidate row
                new_row = {
                    'state': state,
                    'county': county,
                    'geoid': geoid,
                    'total_votes': total_votes,
                    'party': party,
                    'votes': correct_votes,
                    'percentage': (
                        correct_votes /
                        total_votes *
                        100
                    )
                }

                # Add the new row to the dataset
                data = pd.concat(
                    [
                        data,
                        pd.DataFrame([new_row])
                    ],
                    ignore_index=True
                )

    # Recalculate every percentage after corrections
    data['percentage'] = (
        data['votes'] /
        data['total_votes'] *
        100
    )

    return data

def create_repair_report(data, year, filename):


    report = []

    totals = (
        data.groupby(
            ['state', 'county']
        )
        .agg(
            total_votes=('total_votes', 'first'),
            candidate_votes=('votes', 'sum')
        )
        .reset_index()
    )

    totals['difference'] = (
        totals['total_votes'] -
        totals['candidate_votes']
    )

    for _, row in totals.iterrows():

        if row['difference'] == 0:
            status = 'OK'

        elif row['difference'] > 0:
            status = 'MISSING VOTES'

        else:
            status = 'EXCESS VOTES'

        report.append([
            year,
            row['state'],
            row['county'],
            row['total_votes'],
            row['candidate_votes'],
            row['difference'],
            status
        ])

    report = pd.DataFrame(
        report,
        columns=[
            'year',
            'state',
            'county',
            'total_votes',
            'candidate_votes',
            'vote_difference',
            'status'
        ]
    )

    report.to_csv(
        filename,
        index=False
    )

    print(
        f"Repair report saved as {filename}"
    )

def main():

    print("Election Data Repair Tool")
    print("-------------------------")

    # Ask for the original CSV
    data_file = input(
        "CSV to repair: "
    ).strip()

    # Ask for the corrections CSV
    corrections_file = input(
        "Corrections CSV: "
    ).strip()

    # Ask for the election year
    year = int(
        input(
            "Election year: "
        )
    )

    # Ask where to save the corrected CSV
    output_file = input(
        "Corrected CSV filename: "
    ).strip()

    # Ask where to save the repair report
    report_file = input(
        "Repair report filename: "
    ).strip()

    # Load the original election data
    data = pd.read_csv(
        data_file
    )

    # Apply the verified corrections
    data = apply_corrections(
        data,
        corrections_file,
        year
    )

    # Save the corrected election data
    data.to_csv(
        output_file,
        index=False
    )

    print(
        f"Corrected CSV saved as {output_file}"
    )

    # Create a report showing what remains after repair
    create_repair_report(
        data,
        year,
        report_file
    )

if __name__ == '__main__':
    main()