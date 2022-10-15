import datetime
import sys

import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)


def count_pe_ce(row, count_string):
    """
    To Count PE stocks and CE stocks in each row
    :param row: Row in the CSV file
    :param count_string: String to be counted, 'CE' or 'PE'
    :return: returns the number of stocks containing the count string
    """
    stocks = row['stocks'].split(";")
    count = 0
    for i in stocks:
        if i[-2:] == count_string:
            count += 1
    return count


def find_stock_list_pos(str_line):
    """
    Since the stocks are also comma separated in the source file, we are formatting the stocks string to be separated
    by ';'. To acheieve this we need to know from where the stocks start in the file row.
    :param str_line: Each line in the file
    :return: str position from where the stocks start
    """
    n = 0
    p = 0
    for i in range(2):
        p = str_line.find(",")
        n += p
        str_line = str_line[p + 1:]
    return n + 1


month_num_map = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                 '7': 7, '8': 8, '9': 9, 'O': 10, 'N': 11, 'D': 12}


def calculate_current_and_future_stocks(row):
    """
    Each stock comes with an expiration date, a Thursday or Wednesday (incase Thursday is a holiday).
    We are calculating the number of stocks that expires in the current week, and he number of stocks that expires later.
    :param row: Each row in the file
    :return: Number of stocks expiring in the same week, Number of stocks expiring later.
    """
    stock_list = row['stocks'].split(";")
    current_week = 0
    future_week = 0
    for stock in stock_list:
        date_string = stock[len('NFO-OPT:NIFTY'):][:5]
        stock_date = datetime.date(int('20'+date_string[:2]), month_num_map[date_string[2]], int(date_string[-2:]))
        current_date_str = row['date_time'][:11]
        current_date = datetime.datetime.strptime(current_date_str, "%d %b %Y").date()

        delta = stock_date - current_date
        if delta.days < 7:
            current_week += 1
        else:
            future_week += 1

    return [current_week, future_week]


def test_counts(row):
    """
    Testing part. We are making sure our counts match with the total number of stocks
    :param row: Each row in our dataframe
    :return: Boolean. True if the counts match, False if it doesn't.
    """
    row['no_of_stocks'] = int(row['no_of_stocks'])
    res = False
    if row['current_week_stock_count'] + row['future_week_stock_count'] == row['no_of_stocks']:
        res = True
    if row['pe_count'] + row['ce_count'] == row['no_of_stocks']:
        res = res and True

    return res


class NiftyStockCounter:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_nifty_file_to_df(self):
        """
        To read the input file passed as command line argument and create a dataframe.
        :return: A pandas dataframe.
        """
        headers = ["date_time", "no_of_stocks", "stocks"]

        fp = open(self.file_path, 'r')
        l = []
        for line in fp.readlines():
            line = line.strip()
            pos = find_stock_list_pos(line)
            rep_string = line[pos + 1:].replace(",", ";")  # Replacing ',' with ';' for the stock list
            line = line[:pos + 1] + rep_string
            l.append(line.split(","))

        df = pd.DataFrame(l, columns=headers)
        return df

    def run_main(self):
        """
        A method to run all our operations in order. Finally all the aggregated data is written as a csv file.
        :return: N/A
        """
        nifty_df = self.read_nifty_file_to_df()
        nifty_df['pe_count'] = nifty_df.apply(lambda row: count_pe_ce(row, 'PE'), axis=1)
        nifty_df['ce_count'] = nifty_df.apply(lambda row: count_pe_ce(row, 'CE'), axis=1)
        nifty_df['weekly_count'] = nifty_df.apply(lambda row: calculate_current_and_future_stocks(row), axis = 1)
        nifty_df['current_week_stock_count'] = nifty_df.apply(lambda row: row['weekly_count'][0], axis=1)
        nifty_df['future_week_stock_count'] = nifty_df.apply(lambda row: row['weekly_count'][1], axis=1)

        # testing
        nifty_df['test_col'] = nifty_df.apply(lambda row: test_counts(row), axis = 1)
        unmatched_count = nifty_df[nifty_df['test_col'] == False]['test_col'].count()
        if unmatched_count > 0:
            print("Counts doesnt match for %s rows", unmatched_count)
            sys.exit(1)

        final_df = nifty_df[['date_time', 'pe_count', 'ce_count', 'current_week_stock_count', 'future_week_stock_count']]
        final_df.to_csv("data/nifty_monthly_aggregated.csv", header=True, index=False)


if __name__ == "__main__":
    nsc = NiftyStockCounter(sys.argv[1])
    nsc.run_main()
