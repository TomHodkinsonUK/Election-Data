import pandas as pd # type: ignore


def audit_election(filename, year):

    data = pd.read_csv(filename)

    totals = (
        data.groupby(['state', 'county'])['percentage']
        .sum()
        .reset_index()
    )

    problems = totals[
        (totals['percentage'] < 99.9) |
        (totals['percentage'] > 100.1)
    ]

    print(f'\n--- {year} ---')
    print(f'Total counties/districts checked: {len(totals)}')
    print(f'Counties with percentage problems: {len(problems)}')

    print(problems.to_string(index=False))

def audit_votes(filename, year):

    data = pd.read_csv(filename)

    totals = (
        data.groupby(['state', 'county'])
        .agg(
            total_votes=('total_votes', 'first'),
            candidate_votes=('votes', 'sum')
        )
        .reset_index()
    )

    problems = totals[
        totals['total_votes'] != totals['candidate_votes']
    ]

    print(f'\n--- Vote totals: {year} ---')
    print(f'Counties with vote-total problems: {len(problems)}')

    print(problems.to_string(index=False))

def audit_percentages(elections):

    for year, data in elections.items():

        summary = (
            data.groupby(['state', 'county'])
            .agg(
                percentage_total=('percentage', 'sum'),
                total_votes=('total_votes', 'first'),
                candidate_votes=('votes', 'sum')
            )
            .reset_index()
        )

        summary['vote_difference'] = (
            summary['total_votes'] - summary['candidate_votes']
        )

        summary['difference'] = summary['percentage_total'] - 100

        problems = summary[
            summary['difference'].abs() > 1
        ]

        print(f'\n================ {year} ================')

        if problems.empty:
            print('No percentage problems found.')
        else:
            print(
                problems[
                    [
                        'state',
                        'county',
                        'percentage_total',
                        'difference',
                        'total_votes',
                        'candidate_votes',
                        'vote_difference'
                    ]
                ].to_string(index=False)
            )

def main():

    elections = {
        1960: pd.read_csv('data/presidential/csv/1960.csv'),
        1964: pd.read_csv('data/presidential/csv/1964.csv'),
        1968: pd.read_csv('data/presidential/csv/1968.csv'),
        1972: pd.read_csv('data/presidential/csv/1972.csv')
    }

    print('1. Audit percentages')
    print('2. Audit votes')
    print('3. Run both audits')

    choice = input('Choose an audit: ')

    if choice == '1':

        audit_percentages(elections)

    elif choice == '2':

        audit_votes(
            'data/presidential/csv/1960.csv',
            1960
        )

        audit_votes(
            'data/presidential/csv/1964.csv',
            1964
        )

        audit_votes(
            'data/presidential/csv/1968.csv',
            1968
        )

        audit_votes(
            'data/presidential/csv/1972.csv',
            1972
        )

    elif choice == '3':

        audit_percentages(elections)

        audit_votes(
            'data/presidential/csv/1960.csv',
            1960
        )

        audit_votes(
            'data/presidential/csv/1964.csv',
            1964
        )

        audit_votes(
            'data/presidential/csv/1968.csv',
            1968
        )

        audit_votes(
            'data/presidential/csv/1972.csv',
            1972
        )

    else:

        print('Invalid choice.')


if __name__ == '__main__':
    main()

