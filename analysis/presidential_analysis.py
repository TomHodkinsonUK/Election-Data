import pandas as pd

def main():
  data = pd.read_csv('data/presidential/csv/1968.txt')

  print(data.head())


if __name__ == '__main__':
  main()
