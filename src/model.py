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
]


class Model:

    def __init__(self):
        self.cat_map = self.read_category_csv()
        self.transaction_mappings = {}
        self.transactions_df = None
        self.unknown_cat_map = []

    def read_category_csv(self):
        # read in cat mappings (as dict)
        cat_map = {}

        if os.path.isfile(category_path):
            try:
                with open(category_path, mode='r') as csv_file:
                    reader = csv.DictReader(csv_file)
                    for row in reader:
                        key = row[DESCRIPTION]
                        cat_map[key] = row[CATEGORY]
            except KeyError:
                print("Category map file found, but incorrect format")
        return cat_map

    def load_excel(self, filepath: str):
        wb = xw.Book(filepath)
        return wb

    def process_transactions_file(self, filepath: str):
        trans_wb = self.load_excel(filepath)
        sheet = trans_wb.sheets[0]
        self.create_transactions_mapping(sheet)
        transactions = pd.DataFrame(self.transaction_mappings).T
        self.transactions_df = transactions

    def create_transactions_mapping(self, sheet):
        # sht.range('A1:A5').options(ndim=2).value # row
        row = 6
        cell = 'B' + str(row)
        id = 0
        while sheet.range(cell).value is not None:
            self.transaction_mappings[id] = {
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

    def get_final_balance(self):
        '''Get latest balance'''
        return self.transactions_df.iloc[-1][BALANCE]

    def get_total_out(self):
        return self.transactions_df[MONEY_OUT].sum()

    def get_total_in(self):
        return self.transactions_df[MONEY_IN].sum()

    def calc_weekly_savings(self):
        return WEEKLY_BUDGET - self.get_total_out()

    def calc_total_savings(self):
        # accumulative total
        pass

    def get_description_cat(self, description: str):
        for desp, cat in self.cat_map.items():
            if desp in description:
                return cat

    def update_category_mappings(self):
        for row in self.transactions_df.itertuples():
            row_desp = getattr(row, DESCRIPTION)
            category = self.get_description_cat(row_desp)
            # assoc desb with known cat
            if category:
                self.transactions_df.iloc[row.Index][CATEGORY] = category
            else:
                self.unknown_cat_map.append((row.Index, row_desp))

    def calc_category_totals(self):
        unknown_cat_map = []
        for row in self.transactions_df.itertuples():
            row_desp = getattr(row, DESCRIPTION)
            category = self.get_description_cat(row_desp)
            # assoc desb with known cat
            if category:
                self.transactions_df.iloc[row.Index][CATEGORY] = category
            else:
                unknown_cat_map.append((row.Index, row_desp))

        # assoc unknown cats - TODO

        # add totals together
        category_totals = {}
        for cat in CATEGORY_LIST:
            category_totals[cat] = self.transactions_df[self.transactions_df[CATEGORY] == cat][BALANCE].sum()

        return category_totals

    def update_weekly_totals(self, transactions_df):
        cat_totals = self.calc_category_totals(transactions_df)
        # update cat totals

        # update balance, in, out, weekly savings, total savings
        pass

    def update_budget_totals(self):
        # update budget stuff on right
        pass


if __name__ == '__main__':
    model = Model()
    model.process_transactions_file(path)
