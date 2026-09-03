import pandas as pd
import json
import plotly.graph_objects as go


# ======================================================
# MAIN PROGRAM
# ======================================================

def main():

    elections = {
        1960: pd.read_csv('data/house/csv/1960.csv'),
        1962: pd.read_csv('data/house/csv/1962.csv'),
        1964: pd.read_csv('data/house/csv/1964.csv'),
        1966: pd.read_csv('data/house/csv/1966.csv'),
        1968: pd.read_csv('data/house/csv/1968.csv'),
        1970: pd.read_csv('data/house/csv/1970.csv'),
        1972: pd.read_csv('data/house/csv/1972.csv')
    }

    print('1. Highest vote share')
    print('2. Largest vote-share gain')
    print('3. District electoral trajectory')
    print('4. District map')

    choice = input('Choose an analysis: ')

    # --------------------------------------------------
    # HIGHEST VOTE SHARE
    # --------------------------------------------------

    if choice == '1':

        party = input('Party: ')
        year = int(input('Election Year: '))
        state = input(
            'State (leave blank for all states): '
        ).strip().upper()

        result = highest_vote_share(
            elections,
            year,
            party,
            state
        )

        print(
            result[
                [
                    'state',
                    'district',
                    'geoid',
                    'party',
                    'votes',
                    'percentage'
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------
    # LARGEST VOTE-SHARE GAIN
    # --------------------------------------------------

    elif choice == '2':

        party = input('Party: ')
        year_1 = int(input('First Election Year: '))
        year_2 = int(input('Second Election Year: '))
        state = input(
            'State (leave blank for all states): '
        ).strip().upper()

        result = largest_vote_share_gain(
            elections,
            year_1,
            year_2,
            party,
            state
        )

        print(
            result[
                [
                    'state_year_1',
                    'district_year_1',
                    'percentage_year_1',
                    'percentage_year_2',
                    'vote_share_change'
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------
    # DISTRICT TRAJECTORY
    # --------------------------------------------------

    elif choice == '3':

        state = input('State: ').strip().upper()
        district = input('District: ').strip().upper()

        result = district_trajectory(
            elections,
            state,
            district
        )

        print(
            result[
                [
                    'party',
                    'percentage_1960',
                    'percentage_1962',
                    'percentage_1964',
                    'percentage_1966',
                    'percentage_1968',
                    'percentage_1970',
                    'percentage_1972'
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------
    # DISTRICT MAP
    # --------------------------------------------------

    elif choice == '4':

        year = int(input('Election Year: '))

        fig = district_map(
            elections[year],
            year
        )

        fig.show()

    else:

        print('Invalid choice.')


# ======================================================
# HIGHEST VOTE SHARE
# ======================================================

def highest_vote_share(
    elections,
    year,
    party,
    state=None
):

    data = elections[year]

    if state:

        data = data[
            data['state'] == state
        ]

    party_data = data[
        data['party'] == party
    ]

    result = party_data.sort_values(
        'percentage',
        ascending=False
    )

    return result.head(20)


# ======================================================
# LARGEST VOTE-SHARE GAIN
# ======================================================

def largest_vote_share_gain(
    elections,
    year_1,
    year_2,
    party,
    state=None
):

    data_1 = elections[year_1]
    data_2 = elections[year_2]

    if state:

        data_1 = data_1[
            data_1['state'] == state
        ]

        data_2 = data_2[
            data_2['state'] == state
        ]

    party_1 = data_1[
        data_1['party'] == party
    ]

    party_2 = data_2[
        data_2['party'] == party
    ]

    merged = party_1.merge(
        party_2,
        on='geoid',
        suffixes=('_year_1', '_year_2')
    )

    merged['vote_share_change'] = (
        merged['percentage_year_2']
        -
        merged['percentage_year_1']
    )

    result = merged.sort_values(
        'vote_share_change',
        ascending=False
    )

    return result.head(20)


# ======================================================
# DISTRICT ELECTORAL TRAJECTORY
# ======================================================

def district_trajectory(
    elections,
    state,
    district
):

    data_1960 = elections[1960]
    data_1962 = elections[1962]
    data_1964 = elections[1964]
    data_1966 = elections[1966]
    data_1968 = elections[1968]
    data_1970 = elections[1970]
    data_1972 = elections[1972]

    # --------------------------------------------------
    # SELECT DISTRICT
    # --------------------------------------------------

    district_1960 = data_1960[
        data_1960['geoid'] == district
    ]

    district_1962 = data_1962[
        data_1962['geoid'] == district
    ]

    district_1964 = data_1964[
        data_1964['geoid'] == district
    ]

    district_1966 = data_1966[
        data_1966['geoid'] == district
    ]

    district_1968 = data_1968[
        data_1968['geoid'] == district
    ]

    district_1970 = data_1970[
        data_1970['geoid'] == district
    ]

    district_1972 = data_1972[
        data_1972['geoid'] == district
    ]

    # --------------------------------------------------
    # MERGE BY PARTY
    # --------------------------------------------------

    merged = district_1960[
        ['party', 'percentage']
    ].rename(
        columns={
            'percentage': 'percentage_1960'
        }
    )

    merged = merged.merge(
        district_1962[
            ['party', 'percentage']
        ].rename(
            columns={
                'percentage': 'percentage_1962'
            }
        ),
        on='party',
        how='outer'
    )

    merged = merged.merge(
        district_1964[
            ['party', 'percentage']
        ].rename(
            columns={
                'percentage': 'percentage_1964'
            }
        ),
        on='party',
        how='outer'
    )

    merged = merged.merge(
        district_1966[
            ['party', 'percentage']
        ].rename(
            columns={
                'percentage': 'percentage_1966'
            }
        ),
        on='party',
        how='outer'
    )

    merged = merged.merge(
        district_1968[
            ['party', 'percentage']
        ].rename(
            columns={
                'percentage': 'percentage_1968'
            }
        ),
        on='party',
        how='outer'
    )

    merged = merged.merge(
        district_1970[
            ['party', 'percentage']
        ].rename(
            columns={
                'percentage': 'percentage_1970'
            }
        ),
        on='party',
        how='outer'
    )

    merged = merged.merge(
        district_1972[
            ['party', 'percentage']
        ].rename(
            columns={
                'percentage': 'percentage_1972'
            }
        ),
        on='party',
        how='outer'
    )

    return merged

# ======================================================
# DISTRICT MAP
# ======================================================

def district_map(data, year):

    data = data.copy()

    # --------------------------------------------------
    # FIND WINNER IN EACH DISTRICT
    # --------------------------------------------------

    winners = data.loc[
        data.groupby('geoid')['votes'].idxmax()
    ].copy()

    # Make sure percentage is numeric
    winners['percentage'] = pd.to_numeric(
        winners['percentage'],
        errors='coerce'
    )

    # --------------------------------------------------
    # LOAD HISTORICAL GEOJSON
    # --------------------------------------------------

    with open(
        f'data/geography/house/{year}.geojson',
        encoding='utf-8'
    ) as file:

        geojson = json.load(file)

    # --------------------------------------------------
    # CONSTRUCT GEOIDS FOR GEOJSON
    # --------------------------------------------------

    # The CSV uses identifiers such as:
    #
    # AL-01
    # TX-07
    # AK-01
    #
    # Lewis stores the state name and district number
    # separately in the GeoJSON properties.

    state_abbreviations = {

        'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY',
        'District of Columbia': 'DC'
    }

    # Add a geoid to every feature
    for feature in geojson['features']:

        properties = feature.get(
            'properties',
            {}
        )

        state_name = properties.get(
            'statename'
        )

        district_number = properties.get(
            'district'
        )

        state_abbreviation = (
            state_abbreviations.get(
                state_name
            )
        )

        if (
            state_abbreviation is not None
            and district_number is not None
        ):

            try:

                district_number = int(
                    district_number
                )

                properties['geoid'] = (
                    f'{state_abbreviation}-'
                    f'{district_number:02d}'
                )

            except (
                ValueError,
                TypeError
            ):

                properties['geoid'] = None

        else:

            properties['geoid'] = None

    # --------------------------------------------------
    # FIND GEOIDS PRESENT IN GEOJSON
    # --------------------------------------------------

    geojson_geoids = {
        feature['properties'].get('geoid')
        for feature in geojson['features']
    }

    # Keep only districts that exist in the geography
    winners = winners[
        winners['geoid'].isin(
            geojson_geoids
        )
    ].copy()

    print(
        '\nNumber of winning districts:',
        len(winners)
    )

    print(
        'Unique GEOIDs:',
        winners['geoid'].nunique()
    )

    print('\nWinning parties:')

    print(
        winners['party'].value_counts()
    )

    # --------------------------------------------------
    # PARTY COLOUR SCALES
    # --------------------------------------------------

    colour_scales = {

        'Republican': [
            [0, 'rgb(255,235,235)'],
            [0.25, 'rgb(255,190,190)'],
            [0.5, 'rgb(240,120,120)'],
            [0.75, 'rgb(200,50,50)'],
            [1, 'rgb(120,0,0)']
        ],

        'Democratic': [
            [0, 'rgb(235,240,255)'],
            [0.25, 'rgb(190,210,255)'],
            [0.5, 'rgb(120,160,240)'],
            [0.75, 'rgb(50,100,200)'],
            [1, 'rgb(0,40,130)']
        ],

        'American Independent': [
            [0, 'rgb(255,245,220)'],
            [0.25, 'rgb(255,220,150)'],
            [0.5, 'rgb(245,180,70)'],
            [0.75, 'rgb(210,130,20)'],
            [1, 'rgb(160,80,0)']
        ],

        'Other': [
            [0, 'rgb(235,255,235)'],
            [0.25, 'rgb(190,240,190)'],
            [0.5, 'rgb(120,210,120)'],
            [0.75, 'rgb(50,170,50)'],
            [1, 'rgb(0,110,0)']
        ]
    }

    # --------------------------------------------------
    # CREATE MAP
    # --------------------------------------------------

    fig = go.Figure()

    parties = [
        'Republican',
        'Democratic',
        'American Independent',
        'Other'
    ]

    for party in parties:

        subset = winners[
            winners['party'] == party
        ].copy()

        if subset.empty:
            continue

        fig.add_trace(
            go.Choropleth(
                geojson=geojson,

                locations=subset['geoid'],

                featureidkey='properties.geoid',

                z=subset['percentage'],

                zmin=0,
                zmax=100,

                colorscale=colour_scales[party],

                showscale=False,

                marker_line_width=0.2,
                marker_line_color='white',

                name=party,

                customdata=subset[
                    [
                        'district',
                        'state',
                        'party',
                        'votes'
                    ]
                ],

                hovertemplate=(
                    '<b>%{customdata[0]}</b><br>'
                    'State: %{customdata[1]}<br>'
                    'Winner: %{customdata[2]}<br>'
                    'Votes: %{customdata[3]:,}<br>'
                    'Vote share: %{z:.2f}%'
                    '<extra></extra>'
                )
            )
        )

    # --------------------------------------------------
    # MAP SETTINGS
    # --------------------------------------------------

    fig.update_geos(
        visible=False,
        projection_type='albers usa'
    )

    fig.update_layout(

        title=(
            f'House of Representatives '
            f'election, {year}'
        ),

        margin={
            'r': 0,
            't': 50,
            'l': 0,
            'b': 0
        },

        legend_title_text='Winning party'
    )

    return fig


# ======================================================
# RUN PROGRAM
# ======================================================

if __name__ == '__main__':
    main()