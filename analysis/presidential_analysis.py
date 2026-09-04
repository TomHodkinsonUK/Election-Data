import pandas as pd #type: ignore
import plotly.express as px 
import plotly.graph_objects as go
import requests
import json 
 

southern_states = [
  'AL', 'AR', 'FL', 'GA', 'LA', 
  'MS', 'NC', 'SC', 'TN', 'TX', 'VA'
]


def main():

  elections = {
    1960: pd.read_csv('data/presidential/csv/1960.csv'),
    1964: pd.read_csv('data/presidential/csv/1964.csv'),
    1968: pd.read_csv('data/presidential/csv/1968.csv'),
    1972: pd.read_csv('data/presidential/csv/1972.csv')
  }

  print('1. Highest vote share')
  print('2. Largest vote-share gain')
  print('3. County electoral trajectory')
  print('4. County map')

  choice = input('Choose an analysis: ')

  


  if choice == '1':
    party = input('Party: ')
    year = int(input('Election Year: '))
    state = input('State (leave blank for all states): ')
    result = highest_vote_share(elections, year, party, state)
    print(result)
  
  elif choice == '2':
    party = input('Party: ')
    year_1 = int(input('First Election Year: '))
    year_2 = int(input('Second Election Year: '))
    state = input('State (leave blank for all states): ')
    result = largest_vote_share_gain(elections, year_1, year_2, party, state)
    print(result[['state_year_1',
                  'county_year_1',
                  'percentage_year_1',
                  'percentage_year_2',
                  'vote_share_change']])

  elif choice == '3':
    state = input('State: ').upper()
    county = input('County: ').upper()
    

    result = county_trajectory(
      elections, 
      state,
      county, 
    )

    print(result[['party',
                  'percentage_1960',
                  'percentage_1964',
                  'percentage_1968',
                  'percentage_1972']].to_string(index=False))

  elif choice == '4':
    year = int(input('Election Year: '))
    data = elections[year]

    result = county_map(
        data,
        year
    )

    result.write_html(
        f'maps/presidential/{year}.html'
    )

    print(
        f'Presidential map saved to maps/presidential/{year}.html'
    )
  else:
    print('Invalid choice.')
    
def highest_vote_share(elections, year, party, state=None):

  data = elections[year]

  if state: 
    data = data[data['state'] == state]

  party_data = data[data['party'] == party]

  result = party_data.sort_values(
    'percentage',
    ascending=False 
  )

  return result.head(20) 

def largest_vote_share_gain(elections, year_1, year_2, party, state=None):
  data_1 = elections[year_1]
  data_2 = elections[year_2]

  if state:
    data_1 = data_1[data_1['state'] == state]
    data_2 = data_2[data_2['state'] == state]

  party_1 = data_1[data_1['party'] == party]
  party_2 = data_2[data_2['party'] == party]

  merged = party_1.merge(
    party_2, 
    on='geoid', 
    suffixes=('_year_1', '_year_2')
  )
  
  merged['vote_share_change'] = (
    merged['percentage_year_2'] - 
    merged['percentage_year_1']
  )

  result = merged.sort_values(
    'vote_share_change',
    ascending=False
  )


  return result.head(20)

def county_trajectory(elections, state, county):

  data_1960 = elections[1960]
  data_1964 = elections[1964]
  data_1968 = elections[1968]
  data_1972 = elections[1972]

  county_1960 = data_1960[
    (data_1960['state'] == state) &
    (data_1960['county'] == county)
  ]

  county_1964 = data_1964[
    (data_1964['state'] == state) &
    (data_1964['county'] == county)
  ]

  county_1968 = data_1968[
    (data_1968['state'] == state) &
    (data_1968['county'] == county)
  ]

  county_1972 = data_1972[
    (data_1972['state'] == state) &
    (data_1972['county'] == county)
  ]

  merged = county_1960.merge(
    county_1964,
    on='party',
    suffixes=('_1960', '_1964')
  )

  merged = merged.merge(
    county_1968,
    on='party',
    how='outer'
  )

  merged = merged.merge(
    county_1972,
    on='party',
    how='outer'
  )

  merged = merged.rename(columns={
    'percentage_x': 'percentage_1968',
    'percentage_y': 'percentage_1972'
  })
  
  return merged 

def county_map(data, year):

    data = data.copy()

    # --------------------------------------------------
    # PREPARE RICHMOND DATA
    # --------------------------------------------------

    # Convert Richmond GEOID into standard 5-digit FIPS
    data['fips'] = (
        data['geoid'].str[1:3] +
        data['geoid'].str[4:7]
    )

    # Find the winning party in each county
    winners = data.loc[
        data.groupby('geoid')['votes'].idxmax()
    ].copy()

    # Make sure percentage is numeric
    winners['percentage'] = pd.to_numeric(
        winners['percentage'],
        errors='coerce'
    )

    # --------------------------------------------------
    # ALASKA DISTRICT MAPPING
    # --------------------------------------------------

    alaska_mapping = {
        'G0203010': 'PRINCE OF WALES',
        'G0203030': 'KETCHIKAN',
        'G0203050': 'WRANGELL-PETERSBURG',
        'G0203070': 'SITKA',
        'G0203090': 'JUNEAU',
        'G0203110': 'LYNN CANAL-I.S.',
        'G0203130': 'CORDOVA-MCCARTHY',
        'G0203150': 'VALDEZ-C.-W.',
        'G0203170': 'PALMER-W.-T.',
        'G0203190': 'ANCHORAGE',
        'G0203210': 'SEWARD',
        'G0203230': 'KENAI-COOK INLET',
        'G0203250': 'KODIAK',
        'G0203270': 'ALEUTIAN ISLANDS',
        'G0203290': 'BRISTOL BAY',
        'G0203310': 'BETHEL',
        'G0203330': 'KUSKOKWIM',
        'G0203350': 'YUKON-KOYUKUK',
        'G0203370': 'FAIRBANKS',
        'G0203390': 'UPPER YUKON',
        'G0203410': 'BARROW',
        'G0203430': 'KOBUK',
        'G0203440': 'NOME',
        'G0203450': 'WADE-HAMPTON'
    }

    alaska_name_to_geoid = {
        name: geoid
        for geoid, name in alaska_mapping.items()
    }

    # --------------------------------------------------
    # HISTORICAL COUNTY FALLBACKS
    # --------------------------------------------------

    # These historical units need to be matched by their
    # state and county name.
    historical_county_mapping = {
        ('GA', 'BARROW'): 'G1300130',
        ('KS', 'SEWARD'): 'G2001750',
        ('NE', 'SEWARD'): 'G3101590',
        ('WI', 'JUNEAU'): 'G5500570'
    }

    # --------------------------------------------------
    # LOAD HISTORICAL GEOJSON
    # --------------------------------------------------

    with open(
        f'data/geography/{year}.geojson'
    ) as file:

        geojson = json.load(file)

    # --------------------------------------------------
    # CREATE RICHMOND GEOID FOR EACH GEOJSON FEATURE
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
        'Wyoming': 'WY'
    }

    for feature in geojson['features']:

        properties = feature['properties']

        properties['richmond_geoid'] = None

        # ----------------------------------------------
        # NORMAL COUNTIES
        # ----------------------------------------------

        fips = properties.get('fips')

        if fips is not None:

            fips = str(fips).strip()

            if fips.endswith('.0'):
                fips = fips[:-2]

            fips = fips.zfill(5)

            properties['richmond_geoid'] = (
                'G' +
                fips[:2] +
                '0' +
                fips[2:] +
                '0'
            )

        # ----------------------------------------------
        # ALASKA
        # ----------------------------------------------

        name = properties.get('NAME')

        if name is not None:

            name = str(name).strip().upper()

            if name in alaska_name_to_geoid:

                properties['richmond_geoid'] = (
                    alaska_name_to_geoid[name]
                )

    # --------------------------------------------------
    # CHECK FOR HISTORICAL COUNTY FALLBACKS
    # --------------------------------------------------

    for feature in geojson['features']:

        properties = feature['properties']

        state_name = properties.get(
            'STATE_TERR'
        )

        county_name = properties.get(
            'NAME'
        )

        if (
            state_name is not None
            and county_name is not None
        ):

            state_abbreviation = (
                state_abbreviations.get(
                    str(state_name).strip()
                )
            )

            county_name = (
                str(county_name)
                .strip()
                .upper()
            )

            fallback_key = (
                state_abbreviation,
                county_name
            )

            if fallback_key in historical_county_mapping:

                properties['richmond_geoid'] = (
                    historical_county_mapping[
                        fallback_key
                    ]
                )

    # --------------------------------------------------
    # FIND GEOIDS THAT EXIST IN GEOJSON
    # --------------------------------------------------

    geojson_geoids = {
        feature['properties'].get(
            'richmond_geoid'
        )
        for feature in geojson['features']
    }

    # --------------------------------------------------
    # CHECK FOR ANY REMAINING MISSING COUNTIES
    # --------------------------------------------------

    missing_winners = winners[
        ~winners['geoid'].isin(
            geojson_geoids
        )
    ].copy()

    print("\nMissing counties:")

    if missing_winners.empty:

        print("None")

    else:

        print(
            missing_winners[
                [
                    'state',
                    'county',
                    'geoid',
                    'party',
                    'percentage'
                ]
            ].to_string(index=False)
        )

    # Keep matching winners
    winners = winners[
        winners['geoid'].isin(
            geojson_geoids
        )
    ].copy()

    print(
        "\nNumber of winning counties:",
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

    # Dark/base colours used for the legend
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

                featureidkey=(
                    'properties.richmond_geoid'
                ),

                z=subset['percentage'],

                zmin=0,
                zmax=100,

                colorscale=colour_scales[party],

                showscale=False,

                marker_line_width=0.2,
                marker_line_color='white',

                showlegend=False,

                customdata=subset[
                    [
                        'county',
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
            go.Scattergeo(

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

    fig.update_geos(
        visible=False,
        projection_type='albers usa'
    )

    fig.update_layout(

        title=f'Presidential election, {year}',

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

if __name__ == '__main__':
   main()