import sys
import pandas as pd

"""
Modify CSV

Manipulate an input CSV into a new file

`$ python filter_csv.py <input_path> <output_path> <mod_type> <mod_args>`

<input_path> : str
    File path of existing CSV
    Format : Excpets three unmarked columns (timestamp/price/volume) 
             from files downloaded here: http://api.bitcoincharts.com/v1/csv
    Filter : Expects the output of reformat, i.e. two columns named
             'timestamp' (epoch seconds) and 'price' (floats)

<output_path> : str
    File path of output CSV. Will overwrite if already exists.

<mod_type>
    --format :  Reformat the raw CSV. Add column headers, remove 
                the volume column, and purge null values. No mod_args. 
    --filter :  Filter the CSV to specific time intervals, removing rows
                in between intervals. Interval determined by mod_arg.

<mod_args>
    If filtering, add the interval rate as # of seconds

Filter input.csv into output.csv with intervals of 60 seconds
`$ python filter_csv.py input.csv output.csv --filter 60`

Format raw input.csv into nicely formatted output.csv
`$ python filter_csv.py input.csv output.csv --format`
"""


def filter_csv(interval_size: int, input_csv: str, output_csv: str):
    df = pd.read_csv(input_csv)
    df2 = pd.DataFrame(columns=['timestamp', 'price'])
    floor = int(df['timestamp'][0])
    ceiling = floor + interval_size

    for i, row in df.iterrows():
        if i == 0:
            df2 = df2.append(row)
        elif int(row['timestamp']) < ceiling:
            continue
        else:
            ceiling = int(row['timestamp']) + interval_size
            df2 = df2.append(row)
        print(i, end='\r')

    df2.to_csv(output_csv, index=False)


def reformat_csv(input_path: str, output_path: str):
    # Stage 1: Add Columns to headless CSV
    with open(input_path, 'r+') as input, open(output_path, 'w+') as output:
        readcontent = input.read()
        input.close()
        output.write("timestamp,price,volume\n")
        output.write(readcontent)
        output.close()
    # Stage 2: Drop volume column
    df = pd.read_csv(output_path)
    df = df.drop('volume', axis='columns')
    df.to_csv(output_path, index=False)
    # Stage 3: Drop null rows
    df = df.dropna(how='any', axis=0)
    df.to_csv(output_path, index=False)

def validate_csv(input_csv: str, output_file: str, expected_interval: int, margin: int):
    df = pd.read_csv(input_csv)
    print(df.shape)
    print(df.head())
    acceptable_diff = expected_interval * margin
    with open(output_file, 'w+') as file:
        floor = int(df['timestamp'][0])
        for i, row in df.iterrows():
            ceiling = int(row['timestamp'])
            if (ceiling - floor) > acceptable_diff:
                file.writelines([
                    'Bad gap!',
                    f'Row #: {(i + 2)}',
                    f'Floor: {floor}',
                    f'Ceiling: {ceiling}',
                    "========================"
                ])
            floor = ceiling


if __name__ == "__main__":
    try:
        input = sys.argv[1]
        output = sys.argv[2]
        mode = sys.argv[3]
    except:
        print("Bad args read docs!")
        exit()
    if mode == '--filter':
        interval = sys.argv[4]
        filter_csv(int(interval), input, output)
    elif mode == '--format':
        reformat_csv(input, output)
    elif mode == '--validate':
        interval = sys.argv[4]
        validate_csv(input, output)
    else:
        print("Bad args read docs!")
