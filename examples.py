"""Examples

In this module we define some auxiliary functions to generate example settings and transactions.
"""

from project import *


def generate_settings_keys():
    return {
        "locale",
        "currency",
        "saved_categories",
        "saved_monthly_transactions",
        "target_monthly_savings",
        "last_modified",
    }


def generate_example_settings():
    example_locale = "es_ES"
    example_currency = "EUR"
    example_saved_categories = [
        "eating out",
        "gifts",
        "groceries",
        "rent",
        "salary",
        "shopping",
        "transportation",
    ]
    example_saved_monthly_transactions = [
        {
            "Type": "income",
            "Amount": 500.0,
            "Category": "salary",
            "Description": "Salary",
        },
        {
            "Type": "expense",
            "Amount": 100.0,
            "Category": "rent",
            "Description": "Rent",
        },
        {
            "Type": "expense",
            "Amount": 10.0,
            "Category": "transportation",
            "Description": "Monthly Pass",
        },
    ]
    example_target_monthly_savings = 200.0
    example_last_modified = "2000-01-01"
    return {
        "locale": example_locale,
        "currency": example_currency,
        "saved_categories": example_saved_categories,
        "saved_monthly_transactions": example_saved_monthly_transactions,
        "target_monthly_savings": example_target_monthly_savings,
        "last_modified": example_last_modified,
    }


def generate_example_settings_file():
    example_settings = generate_example_settings()
    try:
        load_settings()
        while True:
            user_input = input(
                "WARNING: This will rewrite the current settings.json file. Do you want to proceed? [yes/no]: "
            ).strip()
            if user_input == "yes":
                update_settings(example_settings)
                print("Example settings.json generated.")
                break
            elif user_input == "no":
                break
            else:
                print("Invalid input. Please enter yes or no.")
    except FileNotFoundError:
        init_settings()
        update_settings(example_settings)
        print("Example settings.json generated.")


def generate_transaction_headers():
    return [
        "ID",
        "Date",
        "Type",
        "Amount",
        "Category",
        "Frequency",
        "Description",
    ]


def generate_example_transactions():
    transaction_1 = {
        "ID": "1",
        "Date": "2000-01-01",
        "Type": "income",
        "Amount": 500.0,
        "Category": "salary",
        "Frequency": "monthly",
        "Description": "Salary",
    }
    transaction_2 = {
        "ID": "2",
        "Date": "2000-01-01",
        "Type": "expense",
        "Amount": 100.0,
        "Category": "rent",
        "Frequency": "monthly",
        "Description": "Rent",
    }
    transaction_3 = {
        "ID": "3",
        "Date": "2000-01-01",
        "Type": "expense",
        "Amount": 1.0,
        "Category": "eating out",
        "Frequency": "one-time",
        "Description": "Coffee",
    }
    transaction_4 = {
        "ID": "4",
        "Date": "2000-01-01",
        "Type": "expense",
        "Amount": 10.0,
        "Category": "transportation",
        "Frequency": "monthly",
        "Description": "Monthly Pass",
    }
    transaction_5 = {
        "ID": "5",
        "Date": "2000-01-06",
        "Type": "expense",
        "Amount": 7.0,
        "Category": "groceries",
        "Frequency": "one-time",
        "Description": "Groceries",
    }
    transaction_6 = {
        "ID": "6",
        "Date": "2000-01-06",
        "Type": "income",
        "Amount": 4.0,
        "Category": "gifts",
        "Frequency": "one-time",
        "Description": "Christmas gift",
    }
    transaction_7 = {
        "ID": "7",
        "Date": "2000-01-13",
        "Type": "expense",
        "Amount": 5.0,
        "Category": "gifts",
        "Frequency": "one-time",
        "Description": "Birthday gift",
    }
    transaction_8 = {
        "ID": "8",
        "Date": "2000-01-16",
        "Type": "expense",
        "Amount": 1.0,
        "Category": "eating out",
        "Frequency": "one-time",
        "Description": "Coffee",
    }
    transaction_9 = {
        "ID": "9",
        "Date": "2000-01-16",
        "Type": "expense",
        "Amount": 7.0,
        "Category": "shopping",
        "Frequency": "one-time",
        "Description": "",
    }
    transaction_10 = {
        "ID": "10",
        "Date": "2000-01-16",
        "Type": "expense",
        "Amount": 4.0,
        "Category": "eating out",
        "Frequency": "one-time",
        "Description": "Lunch",
    }
    transaction_11 = {
        "ID": "11",
        "Date": "2000-01-16",
        "Type": "expense",
        "Amount": 1.0,
        "Category": "eating out",
        "Frequency": "one-time",
        "Description": "Coffee",
    }
    transaction_12 = {
        "ID": "12",
        "Date": "2000-01-21",
        "Type": "expense",
        "Amount": 4.0,
        "Category": "eating out",
        "Frequency": "one-time",
        "Description": "Dinner",
    }
    transaction_13 = {
        "ID": "13",
        "Date": "2000-01-27",
        "Type": "expense",
        "Amount": 6.0,
        "Category": "groceries",
        "Frequency": "one-time",
        "Description": "Groceries",
    }
    transaction_14 = {
        "ID": "14",
        "Date": "1999-12-03",
        "Type": "expense",
        "Amount": 4.0,
        "Category": "groceries",
        "Frequency": "one-time",
        "Description": "Groceries",
    }
    transaction_287 = {
        "ID": "287",
        "Date": "1992-07-08",
        "Type": "expense",
        "Amount": 30.0,
        "Category": "stationery",
        "Frequency": "one-time",
        "Description": "",
    }
    transaction_15 = {
        "ID": "15",
        "Date": "1999-12-17",
        "Type": "expense",
        "Amount": 3.0,
        "Category": "eating out",
        "Frequency": "one-time",
        "Description": "Lunch",
    }
    transaction_16 = {
        "ID": "16",
        "Date": "1999-12-23",
        "Type": "expense",
        "Amount": 5.0,
        "Category": "groceries",
        "Frequency": "one-time",
        "Description": "Groceries",
    }
    transaction_17 = {
        "ID": "17",
        "Date": "1999-12-01",
        "Type": "income",
        "Amount": 500.0,
        "Category": "salary",
        "Frequency": "monthly",
        "Description": "Salary",
    }
    transaction_18 = {
        "ID": "18",
        "Date": "1999-12-01",
        "Type": "expense",
        "Amount": 100.0,
        "Category": "rent",
        "Frequency": "monthly",
        "Description": "Rent",
    }
    transaction_19 = {
        "ID": "19",
        "Date": "2000-02-03",
        "Type": "expense",
        "Amount": 1.0,
        "Category": "eating out",
        "Frequency": "one-time",
        "Description": "Coffee",
    }
    transaction_20 = {
        "ID": "20",
        "Date": "2000-02-05",
        "Type": "expense",
        "Amount": 2.0,
        "Category": "eating out",
        "Frequency": "one-time",
        "Description": "Breakfast",
    }
    return [
        transaction_1,
        transaction_2,
        transaction_3,
        transaction_4,
        transaction_5,
        transaction_6,
        transaction_7,
        transaction_8,
        transaction_9,
        transaction_10,
        transaction_11,
        transaction_12,
        transaction_13,
        transaction_14,
        transaction_287,
        transaction_15,
        transaction_16,
        transaction_17,
        transaction_18,
        transaction_19,
        transaction_20,
    ]


def generate_example_transactions_file():
    example_transactions = generate_example_transactions()
    for transaction in example_transactions:
        del transaction["ID"]
    try:
        transactions = load_transactions()
        while True:
            user_input = input(
                "WARNING: This will rewrite the current transactions.csv file. Do you want to proceed? [yes/no]: "
            ).strip()
            if user_input == "yes":
                for transaction in load_transactions():
                    delete_transaction(transaction["ID"])
                for transaction in example_transactions:
                    save_transaction(transaction)
                print("Example transactions.csv generated.")
                break
            elif user_input == "no":
                break
            else:
                print("Invalid input. Please enter yes or no.")
    except FileNotFoundError:
        init_transactions()
        for transaction in example_transactions:
            save_transaction(transaction)
        print("Example transactions.csv generated.")
