import xlwings as xw
import pandas as pd
import csv
import os.path

path = r'..\data\jan-feb-2018.xlsx'
category_path = r'..\data\category-mappings.csv'
sheet = 'transactions'
DATE = 'date'
DESCRIPTION = 'description'
MONEY_IN = 'money in'
MONEY_OUT = 'money out'
BALANCE = 'balance'
CATEGORY = 'category'

START_ROW = '6'

transaction_mappings = {}
WEEKLY_BUDGET = 100  # TODO - remove hardcode
CATEGORY_LIST = [
    'cash',
    'food/ house',
    'takeout',
    'social',
    'birthdays/ occasions',
    'other',
    'education',
    'travel',
    'sport',
    'clothes',
]


def read_category_csv():
    # read in cat mappings (as dict)
    cat_map = {}

    if os.path.isfile(category_path):
        try:
            reader = csv.DictReader(category_path)
            for row in reader:
                print(row)
                key = row[DESCRIPTION]
                cat_map[key] = row[CATEGORY]
        except KeyError:
            print("Category map file found, but incorrect format")
    return cat_map


cat_map = read_category_csv()


def load_excel(filepath: str):
    wb = xw.Book(filepath)
    return wb


def process_transactions_file(filepath: str):
    trans_wb = load_excel(filepath)
    sheet = trans_wb.sheets[0]
    create_transactions_mapping(sheet)
    transactions = pd.DataFrame(transaction_mappings).T
    return transactions


def create_transactions_mapping(sheet):
    # sht.range('A1:A5').options(ndim=2).value # row
    row = 6
    cell = 'B' + str(row)
    id = 0
    while sheet.range(cell).value is not None:
        transaction_mappings[id] = {
            DATE: sheet.range('B' + str(row)).value,
            DESCRIPTION: sheet.range('D' + str(row)).value,
            MONEY_IN: sheet.range('F' + str(row)).value,
            MONEY_OUT: sheet.range('G' + str(row)).value,
            BALANCE: sheet.range('H' + str(row)).value,
            CATEGORY: None,
        }
        row += 1
        id += 1
        cell = 'B' + str(row)


def get_final_balance():
    '''Get latest balance'''
    return transactions_df.iloc[-1][BALANCE]


def get_total_out():
    return transactions_df[MONEY_OUT].sum()


def get_total_in():
    return transactions_df[MONEY_IN].sum()


def calc_weekly_savings():
    return WEEKLY_BUDGET - get_total_out()


def calc_total_savings():
    # accumulative total
    pass


def get_description_cat(description: str):
    for desp, cat in cat_map.items():
        if desp in description:
            return cat


def calc_category_totals(transactions_df):
    unknown_cat_map = []
    for row in transactions_df.itertuples():
        row_desp = getattr(row, DESCRIPTION)
        category = get_description_cat(row_desp)
        # assoc desb with known cat
        if category:
            transactions_df.iloc[row.Index][CATEGORY] = category
        else:
            unknown_cat_map.append((row.Index, row_desp))

    # assoc unknown cats - TODO

    # add totals together
    category_totals = {}
    for cat in CATEGORY_LIST:
        category_totals[cat] = transactions_df[transactions_df[CATEGORY] == cat][BALANCE].sum()

    return category_totals

def update_weekly_totals(transactions_df):
    cat_totals = calc_category_totals(transactions_df)
    # update cat totals

    # update balance, in, out, weekly savings, total savings
    pass

def update_budget_totals():
    # update budget stuff on right
    pass

if __name__ == '__main__':
    transactions_df = process_transactions_file(path)
