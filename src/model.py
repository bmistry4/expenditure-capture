import csv
import os.path

import pandas as pd
import xlwings as xw
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
import pprint

transactions_path = r'..\data\jan-feb-2018.xlsx'
category_path = r'..\data\category-mappings.csv'
budget_path = r'..\data\budget-template.xlsx'

DATE = 'date'
DESCRIPTION = 'description'
MONEY_IN = 'money_in'
MONEY_OUT = 'money_out'
BALANCE = 'balance'
CATEGORY = 'category'

START_ROW = 6
DATE_RANGE_CELL = 'D2'

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
    'beauty',
]


class Model:

    def __init__(self):
        self.cat_map = self.read_category_csv()
        self.transaction_mappings = {}  # todo - make local scope
        self.transactions_df = None
        self.unknown_cat_map = []
        self.one_off_mappings = []  # one time selections when cat different to saved default
        self.id_to_df_index = {}  # id on gui table to df index map

        self.expenditure_file = None
        self.expenditure_sheet = None
        self.update_column = None  # column corresponding to week to update

        self.beginning_date = None

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
        # todo: deal with exception when incorrect file
        trans_wb = self.load_excel(filepath)
        sheet = trans_wb.sheets[0]
        self.create_transactions_mapping(sheet)
        transactions = pd.DataFrame(self.transaction_mappings).T
        self.transactions_df = transactions

        self.add_inital_category_mappings()
        self.set_beginning_date(sheet)

    def load_expenditure_file(self):
        wb = self.load_excel(budget_path)
        sheet = wb.sheets[1]  # todo - search sheet by name so not index hardcoded
        self.update_column = self.find_column_to_update(sheet)
        self.expenditure_sheet = sheet

    def find_column_to_update(self, sheet):
        # returns column value corresponding to the correct week
        column = 'A'
        row = '6'
        cell = column + row
        while sheet.range(cell).value is not None:
            # fixme : limitation - only works till Z then goes to invalid [ not AA
            column = chr(ord(column) + 1)
            cell = column + row
        return column

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

    def set_beginning_date(self, sheet):
        ' gets the date of the week beginning'
        # 01/01/2018 to 01/02/2018 returns 01/01/2018
        self.beginning_date = sheet.range(DATE_RANGE_CELL).value.split(' to ')[0]

    def get_final_balance(self):
        '''Get latest balance'''
        return self.transactions_df.iloc[-1][BALANCE]

    def get_total_out(self):
        return self.transactions_df[MONEY_OUT].sum()

    def get_total_in(self):
        return self.transactions_df[MONEY_IN].sum()

    def calc_weekly_savings(self, weekly_spendings):
        ''' Will only consider desp with assoc cats. So please elect transactions not considered as the cause be large
        transfers which do not want to be considered '''
        return WEEKLY_BUDGET - weekly_spendings

    def calc_total_savings(self, weekly_savings):
        '''return accumulative total'''

        # if first week savings will be the weekly saving for that week
        if self.update_column is 'B':
            return weekly_savings
        else:
            prev_week_col = chr(ord(self.update_column) - 1)
            current_total = self.expenditure_sheet.range(prev_week_col + '21').value
            return float(current_total) + float(weekly_savings)

    def get_description_cat(self, description: str):
        for desp, cat in self.cat_map.items():
            if desp.lower() in description.lower():
                return cat

    def add_inital_category_mappings(self):
        for row in self.transactions_df.itertuples():
            row_desp = getattr(row, DESCRIPTION)
            category = self.get_description_cat(row_desp)
            # assoc desb with known cat
            if category:
                self.transactions_df.iloc[row.Index][CATEGORY] = category
            else:
                self.unknown_cat_map.append((row.Index, row_desp))

    def calc_category_totals(self):
        # add totals together
        category_totals = {}
        for cat in CATEGORY_LIST:
            category_totals[cat] = self.transactions_df[self.transactions_df[CATEGORY] == cat][MONEY_OUT].sum()

        pprint.pprint(category_totals)
        return category_totals

    def update_weekly_totals(self):
        # updates week cell
        self.expenditure_sheet.range(self.update_column + '4').value = self.beginning_date

        # updates category totals
        cat_totals = self.calc_category_totals()
        row = START_ROW
        cat_heading_cell = 'A' + str(row)
        while self.expenditure_sheet.range(cat_heading_cell).value is not None:
            self.expenditure_sheet.range(self.update_column + str(row)).value = cat_totals[
                self.expenditure_sheet.range(cat_heading_cell).value]
            row += 1
            cat_heading_cell = 'A' + str(row)

        # update balance, in, out, weekly savings, total savings
        weekly_spending = sum(cat_totals.values())
        weekly_savings = self.calc_weekly_savings(weekly_spending)
        self.expenditure_sheet.range(self.update_column + '19').value = weekly_spending
        self.expenditure_sheet.range(self.update_column + '20').value = weekly_savings
        self.expenditure_sheet.range(self.update_column + '21').value = self.calc_total_savings(weekly_savings)

        # balance
        self.expenditure_sheet.range(self.update_column + '23').value = self.get_final_balance()

        # totals for each category
        self.update_budget_totals()

    def update_budget_totals(self):
        # TODO - test
        # update budget stuff on right
        cat_row = START_ROW
        while self.expenditure_sheet.range('A' + str(cat_row)).value is not None:
            week_col = 'B'
            cat_total = 0

            cell_value = self.expenditure_sheet.range(week_col + str(cat_row)).value
            while cell_value is not None:
                cat_total += float(cell_value)
                week_col = chr(ord(week_col) + 1)
                new_cell = week_col + str(cat_row)
                cell_value = self.expenditure_sheet.range(new_cell).value
            # update total value for category row
            self.expenditure_sheet.range('R' + str(cat_row)).value = cat_total
            cat_row += 1

    def add_transactions_rows(self, table):
        table_index = 0
        for row in self.transactions_df.itertuples():
            # only account for costings, not savings
            if getattr(row, MONEY_OUT) is not None:
                desp = getattr(row, DESCRIPTION)
                cat = getattr(row, CATEGORY)
                if cat is None:
                    spinner_text = 'Please select...'
                    desp_cell_color = [1, 0, 0, 0.5]
                else:
                    spinner_text = cat
                    desp_cell_color = [0, 1, 0, 0.2]

                table.add_row([TextInput, {'text': desp,
                                           'color_widget': desp_cell_color,
                                           # 'color_click': [0.2, 0.3, 0.5, 0.5]
                                           }],
                              [Spinner, {'text': spinner_text,
                                         # 'color_click': [0.23, 0.24, .5, 1],
                                         'values': CATEGORY_LIST,
                                         }])
                self.id_to_df_index[table_index] = getattr(row, "Index")
                table_index += 1

    def update_categories(self, table_cells):
        # iterate through all cells in gui and update model dataframe
        for table_id, row in enumerate(table_cells):
            df_cat = self.transactions_df.iloc[self.id_to_df_index[table_id]][CATEGORY]
            # if one-off category (i.e. a different category is chosen to the usual one for that desp)
            # one-offs do not cover transaction desps which have never been seen
            if df_cat != row[1].text and df_cat is not None:
                self.one_off_mappings.append(row[1].text)
            self.transactions_df.iloc[self.id_to_df_index[table_id]][CATEGORY] = row[1].text


if __name__ == '__main__':
    model = Model()
    model.process_transactions_file(transactions_path)
