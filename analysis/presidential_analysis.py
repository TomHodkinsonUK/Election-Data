import pandas as pd #type: ignore

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


if __name__ == '__main__':
  main()
