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

    result.show()

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

    # Find the winning party in each county/district
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
        'G0203010': 'Prince of Wales',
        'G0203030': 'Ketchikan',
        'G0203050': 'Wrangell-Petersburg',
        'G0203070': 'Sitka',
        'G0203090': 'Juneau',
        'G0203110': 'Lynn Canal-I.S.',
        'G0203130': 'Cordova-McCarthy',
        'G0203150': 'Valdez-C.-W.',
        'G0203170': 'Palmer-W.-T.',
        'G0203190': 'Anchorage',
        'G0203210': 'Seward',
        'G0203230': 'Kenai-Cook Inlet',
        'G0203250': 'Kodiak',
        'G0203270': 'Aleutian Islands',
        'G0203290': 'Bristol Bay',
        'G0203310': 'Bethel',
        'G0203330': 'Kuskokwim',
        'G0203350': 'Yukon-Koyukuk',
        'G0203370': 'Fairbanks'
    }

    # --------------------------------------------------
    # LOAD HISTORICAL GEOJSON
    # --------------------------------------------------

    with open(
        f'data/geography/{year}.geojson'
    ) as file:

        geojson = json.load(file)

    # --------------------------------------------------
    # MATCH RICHMOND DATA TO HISTORICAL GEOJSON
    # --------------------------------------------------

    # Normal counties are matched using FIPS.
    #
    # Alaska is different because Richmond uses
    # election-district GEOIDs while Newberry uses
    # historical district names.

    geojson_fips = {
        feature['properties'].get('fips')
        for feature in geojson['features']
    }

    geojson_names = {
        feature['properties'].get('NAME')
        for feature in geojson['features']
    }

    # Standard counties
    standard_winners = winners[
        winners['fips'].isin(geojson_fips)
    ].copy()

    # Alaska districts
    alaska_winners = winners[
        winners['geoid'].isin(alaska_mapping)
    ].copy()

    alaska_winners['historical_name'] = (
        alaska_winners['geoid'].map(alaska_mapping)
    )

    alaska_winners = alaska_winners[
        alaska_winners['historical_name'].isin(geojson_names)
    ].copy()

    # --------------------------------------------------
    # CREATE COLOUR SCALES
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

        # --------------------------------------------------
        # STANDARD COUNTIES
        # --------------------------------------------------

        subset = standard_winners[
            standard_winners['party'] == party
        ].copy()

        if not subset.empty:

            fig.add_trace(
                go.Choropleth(
                    geojson=geojson,

                    locations=subset['fips'],

                    featureidkey='properties.fips',

                    z=subset['percentage'],

                    zmin=0,
                    zmax=100,

                    colorscale=colour_scales[party],

                    showscale=False,

                    marker_line_width=0.2,
                    marker_line_color='white',

                    name=party,

                    customdata=subset[
                        ['county', 'state', 'party', 'votes']
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
        # ALASKA
        # --------------------------------------------------

        alaska_subset = alaska_winners[
            alaska_winners['party'] == party
        ].copy()

        if not alaska_subset.empty:

            # Get the actual Newberry names
            alaska_locations = (
                alaska_subset['historical_name']
            )

            # Create a temporary GeoJSON containing
            # only the Alaska features for this party.
            alaska_geojson = {
                'type': 'FeatureCollection',
                'features': [
                    feature
                    for feature in geojson['features']
                    if feature['properties'].get('NAME')
                    in alaska_locations.tolist()
                ]
            }

            fig.add_trace(
                go.Choropleth(
                    geojson=alaska_geojson,

                    locations=alaska_subset[
                        'historical_name'
                    ],

                    featureidkey='properties.NAME',

                    z=alaska_subset['percentage'],

                    zmin=0,
                    zmax=100,

                    colorscale=colour_scales[party],

                    showscale=False,

                    marker_line_width=0.2,
                    marker_line_color='white',

                    name=party,

                    showlegend=False,

                    customdata=alaska_subset[
                        ['county', 'state', 'party', 'votes']
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

    # Dummy traces create the legend entries.
    # The actual map traces have the same names.

    for party, symbol in [
        ('Republican', '●'),
        ('Democratic', '●'),
        ('American Independent', '●'),
        ('Other', '●')
    ]:

        fig.add_trace(
            go.Scattergeo(
                lon=[None],
                lat=[None],
                mode='markers',
                marker=dict(size=10),
                name=party,
                showlegend=True,
                hoverinfo='skip'
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
