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

    winners['percentage'] = pd.to_numeric(
        winners['percentage'],
        errors='coerce'
    )

    # --------------------------------------------------
    # LOAD HISTORICAL HOUSE GEOJSON
    # --------------------------------------------------

    with open(
        f'data/geography/house/{year}.geojson'
    ) as file:

        geojson = json.load(file)

    # --------------------------------------------------
    # STATE ABBREVIATIONS
    # --------------------------------------------------

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

    # --------------------------------------------------
    # CREATE HOUSE GEOID FOR EACH GEOJSON FEATURE
    # --------------------------------------------------

    for feature in geojson['features']:

        properties = feature['properties']

        state_name = properties.get(
            'statename'
        )

        district_number = properties.get(
            'district'
        )

        state = state_abbreviations.get(
            state_name
        )

        if (
            state is not None
            and district_number is not None
        ):

            try:

                district_number = int(
                    district_number
                )

                properties['house_geoid'] = (
                    f'{state}-{district_number:02d}'
                )

            except (
                ValueError,
                TypeError
            ):

                properties['house_geoid'] = None

        else:

            properties['house_geoid'] = None

    # --------------------------------------------------
    # AVAILABLE GEOIDS
    # --------------------------------------------------

    geojson_geoids = {
        feature['properties'].get(
            'house_geoid'
        )
        for feature in geojson['features']
    }

    # --------------------------------------------------
    # MATCH ELECTION GEOIDS TO GEOJSON
    #
    # Lewis uses XX-00 for an at-large seat.
    # Election data uses XX-01.
    # --------------------------------------------------

    winners['map_geoid'] = winners['geoid']

    for index, row in winners.iterrows():

        election_geoid = row['geoid']

        # Normal district
        if election_geoid in geojson_geoids:
            continue

        # At-large district
        state = str(
            row['state']
        ).strip().upper()

        at_large_geoid = (
            f'{state}-00'
        )

        if at_large_geoid in geojson_geoids:

            winners.at[
                index,
                'map_geoid'
            ] = at_large_geoid

        else:

            winners.at[
                index,
                'map_geoid'
            ] = None

    # --------------------------------------------------
    # CHECK FOR MISSING DISTRICTS
    # --------------------------------------------------

    missing_winners = winners[
        winners['map_geoid'].isna()
    ].copy()

    print("\nMissing districts:")

    if missing_winners.empty:

        print("None")

    else:

        print(
            missing_winners[
                [
                    'state',
                    'district',
                    'geoid',
                    'party',
                    'percentage'
                ]
            ].to_string(index=False)
        )

    winners = winners[
        winners['map_geoid'].notna()
    ].copy()

    print(
        "\nNumber of winning districts:",
        len(winners)
    )

    print(
        "Unique GEOIDs:",
        winners['geoid'].nunique()
    )

    print("\nWinning parties:")

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
    # PARTY LEGEND
    # --------------------------------------------------

    legend_colours = {

        'Republican': 'rgb(180,40,40)',
        'Democratic': 'rgb(40,90,190)',
        'American Independent': 'rgb(220,140,25)',
        'Other': 'rgb(40,150,40)'
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

    # --------------------------------------------------
    # CREATE A SMALL GEOJSON FOR EACH PARTY
    #
    # This is the important memory fix.
    # --------------------------------------------------

    for party in parties:

        subset = winners[
            winners['party'] == party
        ].copy()

        if subset.empty:
            continue

        party_geoids = set(
            subset['map_geoid']
        )

        party_features = [
            feature
            for feature in geojson['features']
            if feature['properties'].get(
                'house_geoid'
            ) in party_geoids
        ]

        party_geojson = {
            'type': 'FeatureCollection',
            'features': party_features
        }

        # --------------------------------------------------
        # MAP THIS PARTY
        # --------------------------------------------------

        fig.add_trace(
            go.Choroplethmap(

                geojson=party_geojson,

                locations=subset[
                    'map_geoid'
                ],

                featureidkey=(
                    'properties.house_geoid'
                ),

                z=subset[
                    'percentage'
                ],

                zmin=0,
                zmax=100,

                colorscale=colour_scales[
                    party
                ],

                showscale=False,

                marker=dict(
                    opacity=1,
                    line=dict(
                        width=0.5,
                        color='white'
                    )
                ),

                showlegend=False,

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
    # PARTY LEGEND
    # --------------------------------------------------

    for party in parties:

        fig.add_trace(
            go.Scattermap(

                lon=[None],
                lat=[None],

                mode='markers',

                marker=dict(
                    size=10,
                    color=legend_colours[party]
                ),

                name=party,

                showlegend=True,

                hoverinfo='skip'
            )
        )

    # --------------------------------------------------
    # VOTE-SHARE KEY
    # --------------------------------------------------

    gradient_values = [
        (0.00, '0%'),
        (0.25, '25%'),
        (0.50, '50%'),
        (0.75, '75%'),
        (1.00, '100%')
    ]

    key_y_positions = {
        'Republican': 0.16,
        'Democratic': 0.10,
        'American Independent': 0.04,
        'Other': -0.02
    }

    for party in parties:

        y = key_y_positions[party]

        fig.add_annotation(
            x=0.78,
            y=y + 0.018,
            xref='paper',
            yref='paper',
            text=party,
            showarrow=False,
            font=dict(size=10)
        )

        scale = colour_scales[party]

        for i in range(5):

            if i == 0:
                x0 = 0.86
                x1 = 0.884

            elif i == 1:
                x0 = 0.884
                x1 = 0.908

            elif i == 2:
                x0 = 0.908
                x1 = 0.932

            elif i == 3:
                x0 = 0.932
                x1 = 0.956

            else:
                x0 = 0.956
                x1 = 0.980

            fig.add_shape(

                type='rect',

                xref='paper',
                yref='paper',

                x0=x0,
                x1=x1,

                y0=y,
                y1=y + 0.025,

                fillcolor=scale[i][1],

                line=dict(
                    width=0
                )
            )

        x_positions = [
            0.86,
            0.884,
            0.908,
            0.932,
            0.956
        ]

        for i, (position, label) in enumerate(
            gradient_values
        ):

            fig.add_annotation(

                x=x_positions[i],

                y=y - 0.018,

                xref='paper',
                yref='paper',

                text=label,

                showarrow=False,

                font=dict(size=8)
            )

    # --------------------------------------------------
    # MAP SETTINGS
    # --------------------------------------------------

    fig.update_layout(

        title=(
            f'House of Representatives election, '
            f'{year}'
        ),

        map=dict(
            style='white-bg',
            center=dict(
                lat=39,
                lon=-96
            ),
            zoom=2.6
        ),

        margin={
            'r': 0,
            't': 50,
            'l': 0,
            'b': 0
        },

        legend=dict(
            title='Winning party',
            orientation='v',
            x=0.01,
            y=0.99
        )
    )

    return fig

# ======================================================
# RUN PROGRAM
# ======================================================

if __name__ == '__main__':
    main()