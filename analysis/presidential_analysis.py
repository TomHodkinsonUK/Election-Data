import pandas as pd 

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

  for year, data in elections.items():
    print(f'{year}: {len(data)} rows')


  year = int(input('Election Year: '))
  party = input('Party: ')

  if year not in elections: 
    print('Election year not available.')
    return 
  
  result = highest_vote_share(elections, year, party)

  print(result)

def highest_vote_share(elections, year, party):

  data = elections[year]

  party_data = data[data['party'] == party]

  result = party_data.sort_values(
    'percentage',
    ascending=False 
  )

  return result.head(20) 

def highest_southern(elections, year, party):
  data = elections[year]

  southern_data = data[data['state']isin(southern_states)]
  party_data = southern_data[southern_data['party'] == party]

  result = party_data.sort_values('percentage', ascending=False)

  return result.head(20)
  

  
if __name__ == '__main__':
  main()
