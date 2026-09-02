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


  choice = input('Choose an analysis: ')

  party = input('Party: ')


  if choice == '1':
    year = int(input('Election Year: '))
    state = input('State (leave blank for all states): ')
    result = highest_vote_share(elections, year, party, state)
    print(result)
  
  elif choice == '2':
    year_1 = int(input('First Election Year: '))
    year_2 = int(input('Second Election Year: '))
    state = input('State (leave blank for all states): ')
    result = largest_vote_share_gain(elections, year_1, year_2, party, state)
    print(result[['state_year_1',
                  'county_year_1',
                  'percentage_year_1',
                  'percentage_year_2',
                  'vote_share_change']])


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


if __name__ == '__main__':
  main()
