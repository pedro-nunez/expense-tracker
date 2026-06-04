import os
import re
import json
import csv
import time
from datetime import date
from babel.core import get_global
from babel.dates import format_date
from babel.localedata import locale_identifiers
from babel.numbers import format_currency
from tabulate import tabulate


def main():
    display_greeting()

    try:
        get_settings()
    except FileNotFoundError:
        initialize_settings()
        print("Settings file not found. Default settings file created.")

    try:
        get_transactions()
    except FileNotFoundError:
        initialize_transactions()
        print("Transactions file not found. Empty transactions file created.")

    while True:
        try:
            chosen_main_menu_option = prompt_main_menu()
        except EOFError:
            print()
            break
        match chosen_main_menu_option:
            case "0":
                try:
                    display_current_month_overview()
                except EOFError:
                    print()
                    continue
            case "1":
                try:
                    prompt_add_onetime_expense()
                except EOFError:
                    print()
                    print("Input interrupted.")
                    continue
            case "2":
                try:
                    prompt_add_transaction()
                except EOFError:
                    print()
                    print("Input interrupted.")
                    continue
            case "3":
                try:
                    prompt_modify_transaction()
                except EOFError:
                    print()
                    print("Input interrupted.")
                    continue
            case "4":
                try:
                    prompt_delete_transaction()
                except EOFError:
                    print()
                    print("Input interrupted.")
                    continue
            case "5":
                add_monthly_transactions(date.today().isoformat()[0:7])
                print("Saved monthly transactions added to the current month.")
            case "6":
                try:
                    prompt_month_summary()
                except EOFError:
                    print()
                    print("Input interrupted.")
                    continue
            case "7":
                try:
                    prompt_search_transactions()
                except EOFError:
                    print()
                    print("Input interrupted.")
                    continue
            case "8":
                while True:
                    try:
                        chosen_settings_menu_option = prompt_settings_menu()
                    except EOFError:
                        break
                    match chosen_settings_menu_option:
                        case "0":
                            try:
                                display_settings()
                            except EOFError:
                                print()
                                break
                            break
                        case "1":
                            try:
                                prompt_locale()
                            except EOFError:
                                print()
                                print("Input interrupted.")
                                continue
                            break
                        case "2":
                            try:
                                prompt_currency()
                            except EOFError:
                                print()
                                print("Input interrupted.")
                                continue
                            break
                        case "3":
                            try:
                                prompt_add_category()
                            except EOFError:
                                print()
                                print("Input interrupted.")
                                continue
                            break
                        case "4":
                            try:
                                prompt_delete_category()
                            except EOFError:
                                print()
                                print("Input interrupted.")
                                continue
                            break
                        case "5":
                            try:
                                prompt_add_monthly_transaction()
                            except EOFError:
                                print()
                                print("Input interrupted.")
                                continue
                            break
                        case "6":
                            try:
                                prompt_delete_monthly_transaction()
                            except EOFError:
                                print()
                                print("Input interrupted.")
                                continue
                            break
                        case "7":
                            try:
                                prompt_target_monthly_savings()
                            except EOFError:
                                print()
                                print("Input interrupted.")
                                continue
                            break
                        case "8":
                            break
                        case _:
                            print(
                                "Invalid input. Please enter a number 0-8 and press Enter."
                            )
            case "9":
                try:
                    display_help()
                except EOFError:
                    print()
                    continue
            case "10":
                break
            case _:
                print("Invalid input. Please enter a number 0-10 and press Enter.")
                continue
    display_farewell()


"""DATA LAYER

Reads and writes data in persistent storage:
- Settings in a JSON file.
- Transactions in a CSV file.

Handles structural validation, for example:
- Existence of necessary files.
- Required keys are present and values are of the right type.
- Loaded object is of the right type and expected structure.
- Catch file/parsing exceptions only to re-raise clearer errors.

Does not belong here:
- UI code (input(), print(), etc).
- Logic operations and calculations.
- Raw user-input validation.
- Semantic validation, e.g. checking that amounts are non-negative.
"""

# ==========================================
# SETTINGS HANDLERS
# ==========================================


def init_settings() -> None:
    """
    Creates default settings JSON file.

    :raise FileExistsError: If settings file already exists.
    :return: None
    :rtype: None
    """
    file_name = "settings.json"

    if os.path.exists(file_name):
        raise FileExistsError("Settings file already exists.")

    default_locale = "en_US"
    default_currency = "USD"
    default_saved_categories = []
    default_saved_monthly_transactions = []
    default_target_monthly_savings = 0.0

    default_settings = {
        "locale": default_locale,
        "currency": default_currency,
        "saved_categories": default_saved_categories,
        "saved_monthly_transactions": default_saved_monthly_transactions,
        "target_monthly_savings": default_target_monthly_savings,
        "last_modified": date.today().isoformat(),
    }

    with open(file_name, "w") as file:
        json.dump(default_settings, file, indent=4)


def load_settings() -> dict:
    """
    Loads the settings from a JSON file into a dictionary.

    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: The dictionary with the settings.
    :rtype: dict
    """
    file_name = "settings.json"

    # Check that the file exists.
    if not os.path.exists(file_name):
        raise FileNotFoundError("Settings file not found.")

    with open(file_name, "r") as file:
        loaded_settings = json.load(file)

    # Check that the loaded JSON file is a dictionary.
    if not isinstance(loaded_settings, dict):
        raise ValueError("Settings file does not load into a dictionary.")

    # Check that it contains the expected keys.
    required_keys = {
        "locale",
        "currency",
        "saved_categories",
        "saved_monthly_transactions",
        "target_monthly_savings",
        "last_modified",
    }
    if set(loaded_settings.keys()) != required_keys:
        raise KeyError("Invalid keys in settings.json.")

    # Check that each of the values is of the expected type.
    if not isinstance(loaded_settings["locale"], str):
        raise TypeError("Invalid locale in settings.json.")

    if not isinstance(loaded_settings["currency"], str):
        raise TypeError("Invalid currency in settings.json.")

    if not isinstance(loaded_settings["saved_categories"], list) or not all(
        isinstance(item, str) for item in loaded_settings["saved_categories"]
    ):
        raise TypeError("Invalid list of saved categories in settings.json.")

    if (
        not isinstance(loaded_settings["saved_monthly_transactions"], list)
        or not all(
            isinstance(item, dict)
            for item in loaded_settings["saved_monthly_transactions"]
        )
        or not all(
            item.keys() == {"Type", "Amount", "Category", "Description"}
            for item in loaded_settings["saved_monthly_transactions"]
        )
    ):
        raise TypeError("Invalid list of saved monthly transactions in settings.json.")

    if not all(
        isinstance(item["Type"], str)
        and isinstance(item["Amount"], float)
        and isinstance(item["Category"], str)
        and isinstance(item["Description"], str)
        for item in loaded_settings["saved_monthly_transactions"]
    ):
        raise TypeError("Invalid list of saved monthly transactions in settings.json.")

    if not isinstance(loaded_settings["target_monthly_savings"], float):
        raise TypeError("Invalid target monthly savings in settings.json.")

    if not isinstance(loaded_settings["last_modified"], str):
        raise TypeError("Invalid last modified in settings.json.")

    return loaded_settings


def update_settings(input_settings: dict) -> None:
    """
    Updates the settings.json file with the input settings.

    :param input_settings: The input settings dictionary. It should contain the following keys: locale (a string), currency (a string), saved_categories (a list of strings), saved_monthly_transactions (a list of dictionaries, each with keys "Type", "Amount", "Category", "Description"), target_monthly_savings (a float) and last_modified (a string).
    :type input_settings: dict
    :raise KeyError: If input_settings does not contain the expected keys.
    :raise TypeError: If input settings values are not of the expected type.
    :return: None
    :rtype: None
    """
    file_name = "settings.json"

    # Check that the input_settings dictionary contains the expected keys.
    required_keys = {
        "locale",
        "currency",
        "saved_categories",
        "saved_monthly_transactions",
        "target_monthly_savings",
        "last_modified",
    }
    if set(input_settings.keys()) != required_keys:
        raise KeyError("Invalid setting keys.")

    # Check that the values in input_settings are of the expected type.
    if not isinstance(input_settings["locale"], str):
        raise TypeError("Invalid locale.")

    if not isinstance(input_settings["currency"], str):
        raise TypeError("Invalid currency.")

    if not isinstance(input_settings["saved_categories"], list) or not all(
        isinstance(item, str) for item in input_settings["saved_categories"]
    ):
        raise TypeError("Invalid list of saved categories.")

    if (
        not isinstance(input_settings["saved_monthly_transactions"], list)
        or not all(
            isinstance(item, dict)
            for item in input_settings["saved_monthly_transactions"]
        )
        or not all(
            item.keys() == {"Type", "Amount", "Category", "Description"}
            for item in input_settings["saved_monthly_transactions"]
        )
    ):
        raise TypeError("Invalid list of saved monthly transactions.")

    if not all(
        isinstance(item["Type"], str)
        and isinstance(item["Amount"], float)
        and isinstance(item["Category"], str)
        and isinstance(item["Description"], str)
        for item in input_settings["saved_monthly_transactions"]
    ):
        raise TypeError("Invalid list of saved monthly transactions in settings.json.")

    if not isinstance(input_settings["target_monthly_savings"], float):
        raise TypeError("Invalid target monthly savings.")

    # Create a new settings dictionary, to avoid modifying the input dictionary.
    new_settings = input_settings.copy()
    new_settings["last_modified"] = date.today().isoformat()

    with open(file_name, "w") as file:
        json.dump(new_settings, file, indent=4)


# ==========================================
# TRANSACTION HANDLERS
# ==========================================


def init_transactions() -> None:
    """
    Create the transactions.csv file.

    :raise FileExistsError: If transactions file already exists.
    :return: None
    :rtype: None
    """
    file_name = "transactions.csv"

    if os.path.exists(file_name):
        raise FileExistsError("Transactions file already exists.")

    transaction_headers = [
        "ID",
        "Date",
        "Type",
        "Amount",
        "Category",
        "Frequency",
        "Description",
    ]

    with open(file_name, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=transaction_headers)
        writer.writeheader()


def load_transactions() -> list[dict]:
    """
    Loads the transactions from transactions.csv. Amounts are converted to floats.

    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: A list with one dictionary for each transaction in the CSV transactions file. All values in the dictionary are left as strings, except for the amount, which is converted into a float.
    :rtype: list
    """
    file_name = "transactions.csv"
    if not os.path.exists(file_name):
        raise FileNotFoundError("Transactions file not found.")

    expected_headers = [
        "ID",
        "Date",
        "Type",
        "Amount",
        "Category",
        "Frequency",
        "Description",
    ]

    loaded_transactions = []

    with open(file_name, "r", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != expected_headers:
            raise ValueError("Transactions do not contain the expected headers.")
        for transaction in reader:
            try:
                transaction["Amount"] = float(transaction["Amount"])
            except (ValueError, TypeError):
                raise ValueError("Transaction contains invalid amount.")
            loaded_transactions.append(transaction)

    return loaded_transactions


def save_transaction(input_transaction: dict) -> None:
    """
    Append a new transaction based on input_transaction in the transactions CSV file. A unique ID will be added to the new transaction. Note that amounts will be automatically converted to strings.

    :param input_transaction: Dictionary containing the details of the input transaction. It should contain the following keys: Date, Type, Amount, Category, Frequency, Description. All of them should be strings, except for the Amount, which should be a float.
    :type input_transaction: dict
    :raise FileNotFoundError: If transactions file not found.
    :raise KeyError: If input_transaction contains invalid keys or is missing required keys.
    :raise TypeError: If the values in input_transaction are not of the expected type.
    :return: None
    :rtype: None
    """
    file_name = "transactions.csv"
    transaction_headers = [
        "ID",
        "Date",
        "Type",
        "Amount",
        "Category",
        "Frequency",
        "Description",
    ]

    if not os.path.exists(file_name):
        raise FileNotFoundError("Transactions file not found.")

    # Check that the input_transaction dictionary contains the expected keys.
    required_keys = {
        "Date",
        "Type",
        "Amount",
        "Category",
        "Frequency",
        "Description",
    }
    if set(input_transaction.keys()) != required_keys:
        raise KeyError("Invalid transaction keys.")

    for key in required_keys - {"Amount"}:
        if not isinstance(input_transaction[key], str):
            raise TypeError(f"{key} in input_transaction should be a string.")

    if not isinstance(input_transaction["Amount"], float):
        raise TypeError("Amount in input_transaction should be a float.")

    # Create a new transaction dictionary, to avoid modifying the input transaction.
    new_transaction = input_transaction.copy()
    # Create a unique identifier for the transaction. Nanoseconds are better in case we call save_transaction inside a loop.
    new_id = time.time_ns()
    new_transaction["ID"] = str(new_id)

    with open(file_name, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=transaction_headers)
        writer.writerow(new_transaction)


def delete_transaction(target_id: str) -> None:
    """
    Delete the target transaction.

    :param target_id: The ID of the target transaction.
    :type target_id: str
    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :raise KeyError: If none or several transactions with the given ID are found.
    :return: None
    :rtype: None
    """
    file_name = "transactions.csv"
    transactions = load_transactions()

    target_transactions = [
        transaction for transaction in transactions if transaction["ID"] == target_id
    ]

    if len(target_transactions) == 0:
        raise KeyError("No transaction with the given ID found.")
    elif len(target_transactions) > 1:
        raise KeyError("Several transactions with the given ID found.")
    else:
        new_transactions = [
            transaction
            for transaction in transactions
            if transaction["ID"] != target_id
        ]
        with open(file_name, "w", newline="") as file:
            transaction_headers = [
                "ID",
                "Date",
                "Type",
                "Amount",
                "Category",
                "Frequency",
                "Description",
            ]
            writer = csv.DictWriter(file, fieldnames=transaction_headers)
            writer.writeheader()
            writer.writerows(new_transactions)


def update_transaction(target_id: str, target_key: str, new_value: str | float) -> None:
    """
    Update the target transaction's target key value.

    :param target_id: The ID of the target transaction.
    :type target_id: str
    :param target_key: The key of the value to modify.
    :type target_key: str
    :param new_value: The new value.
    :type new_value: str or float
    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :raise KeyError: If none or several transactions with the given ID are found, or if the target key is not a valid transaction key.
    :raise TypeError: If the new value is not of the correct type.
    :return: None
    :rtype: None
    """
    file_name = "transactions.csv"
    transactions = load_transactions()

    # Check that the target_key is a valid transaction key.
    valid_keys = {
        "Date",
        "Type",
        "Amount",
        "Category",
        "Frequency",
        "Description",
    }
    if target_key not in valid_keys:
        raise KeyError("Invalid transaction key.")

    # Check that the new_value has the correct type
    if target_key == "Amount" and not isinstance(new_value, float):
        raise TypeError("Amount should be a float.")
    elif target_key != "Amount" and not isinstance(new_value, str):
        raise TypeError(f"{target_key} should be a string.")

    target_transactions = [
        transaction for transaction in transactions if transaction["ID"] == target_id
    ]

    if len(target_transactions) == 0:
        raise KeyError("No transaction with the given ID found.")
    elif len(target_transactions) > 1:
        raise KeyError("Several transactions with the given ID found.")
    else:
        for transaction in transactions:
            if transaction["ID"] == target_id:
                transaction[target_key] = new_value
        with open(file_name, "w", newline="") as file:
            transaction_headers = [
                "ID",
                "Date",
                "Type",
                "Amount",
                "Category",
                "Frequency",
                "Description",
            ]
            writer = csv.DictWriter(file, fieldnames=transaction_headers)
            writer.writeheader()
            writer.writerows(transactions)


"""LOGIC LAYER

Bridge between data layer and UI layer:
- Retrieve data from the data layer, process it and pass it to the UI layer.
- Receive user input from UI layer and pass the necessary commands to the data layer.
- Perform calculations on the data.

Handle semantical validation, for example:
- Validity of the various values in a transaction dictionary.
- Validity of dates and amounts.

Does not belong here:
- UI code (input(), print(), etc).
- Raw user-input validation.
- Structural validation, e.g., loaded object is of the right type and expected structure.
"""

# ==========================================
# PROCESS DATA FOR DISPLAY
# ==========================================


def generate_settings_overview() -> list[dict]:
    """
    Generate an overview of the current settings, later to be displayed using tabulate.

    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: The formatted list of settings, each of them represented by a dictionary.
    :rtype: list
    """
    settings = get_settings()

    saved_categories = get_saved_categories()
    formatted_saved_categories = ""
    if len(saved_categories) > 0:
        formatted_saved_categories += saved_categories[0].title()
        for i in range(1, len(saved_categories)):
            formatted_saved_categories += f"\n{saved_categories[i].title()}"

    saved_monthly_transactions = get_saved_monthly_transactions()
    formatted_saved_monthly_transactions = ""
    if len(saved_monthly_transactions) > 0:
        if saved_monthly_transactions[0]["Description"] == "":
            formatted_saved_monthly_transactions += f"{saved_monthly_transactions[0]['Category'].title()}: {custom_format_amount(saved_monthly_transactions[0]['Amount'])} {saved_monthly_transactions[0]['Type']}."
        else:
            formatted_saved_monthly_transactions += f"{saved_monthly_transactions[0]['Description']}: {custom_format_amount(saved_monthly_transactions[0]['Amount'])} {saved_monthly_transactions[0]['Type']}."
        for i in range(1, len(saved_monthly_transactions)):
            if saved_monthly_transactions[i]["Description"] == "":
                formatted_saved_monthly_transactions += f"\n{saved_monthly_transactions[i]['Category'].title()}: {custom_format_amount(saved_monthly_transactions[i]['Amount'])} {saved_monthly_transactions[i]['Type']}."
            else:
                formatted_saved_monthly_transactions += f"\n{saved_monthly_transactions[i]['Description']}: {custom_format_amount(saved_monthly_transactions[i]['Amount'])} {saved_monthly_transactions[i]['Type']}."

    formatted_target_monthly_savings = custom_format_amount(
        get_target_monthly_savings()
    )
    formatted_settings = [
        {"Setting": "Locale", "Value": settings["locale"]},
        {"Setting": "Currency", "Value": settings["currency"]},
        {"Setting": "Saved Categories", "Value": formatted_saved_categories},
        {
            "Setting": "Saved Monthly Transactions",
            "Value": formatted_saved_monthly_transactions,
        },
        {
            "Setting": "Target Monthly Savings",
            "Value": formatted_target_monthly_savings,
        },
        {
            "Setting": "Last Modified (Settings)",
            "Value": custom_format_date(get_last_modified()),
        },
    ]
    return formatted_settings


def generate_saved_monthly_transactions_list() -> list[dict]:
    """
    Generate a formatted list of the saved monthly transactions, later to be displayed using tabulate using headers="keys" and showindex="always".

    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: The formatted list of saved monthly transactions, each of them represented by a dictionary with keys "Type", "Amount", "Category" and "Description".
    :rtype: list
    """
    saved_monthly_transactions = get_saved_monthly_transactions()
    formatted_saved_monthly_transactions = []
    for transaction in saved_monthly_transactions:
        formatted_transaction = transaction.copy()
        formatted_transaction["Type"] = formatted_transaction["Type"].title()
        formatted_transaction["Amount"] = custom_format_amount(
            formatted_transaction["Amount"]
        )
        formatted_transaction["Category"] = formatted_transaction["Category"].title()
        formatted_saved_monthly_transactions.append(formatted_transaction)
    return formatted_saved_monthly_transactions


def generate_transaction_list(
    transaction_list: list[dict], header_list: list[str]
) -> list[dict]:
    """
    Generate a list of transactions formatted according to header_list, later to be displayed using tabulate using headers="keys" and showindex="always".

    :param transaction_list: The transaction list to be formatted.
    :type transaction_list: list
    :param header_list: The list of headers to use as a blueprint to format the transactions.
    :type header_list: list
    :raise FileNotFoundError: If settings.json not found.
    :raise TypeError: If header_list is not a list or if its values are not strings, or if the values in settings.json are not of the expected type.
    :raise KeyError: If the headers do not correspond to a valid set of keys, or if settings.json contains invalid keys or is missing required keys.
    :raise ValueError: If header list contains repetitions, or if settings.json exists but does not load into a dictionary.
    :return: The formatted list of transactions, each of them represented by a dictionary with the keys in header_list.
    :rtype: list
    """
    if not isinstance(header_list, list) or not all(
        isinstance(item, str) for item in header_list
    ):
        raise TypeError("Header list should be a list of strings.")

    valid_keys = {
        "Date",
        "Type",
        "Amount",
        "Category",
        "Frequency",
        "Description",
    }
    if not all(item.title() in valid_keys for item in header_list):
        raise KeyError("Headers do not correspond to a valid set of keys.")

    # Make sure that header_list has no repetitions.
    if len(header_list) != len(set([item.title() for item in header_list])):
        raise ValueError("List of headers contains repetitions.")

    formatted_transaction_list = list(
        map(lambda x: format_transaction(x, header_list), transaction_list)
    )

    return formatted_transaction_list


def generate_month_overview(target_month: str) -> list[dict]:
    """
    Create an overview of the target month, to be later displayed using tabulate.

    :param target_month: The target month in YYYY-MM format.
    :type target_month: str
    :raise FileNotFoundError: If transactions file not found, or if settings.json not found.
    :raise ValueError: If target_month is not a valid month or is not given in the expected format, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount, or if settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type, or if amount is not a float.
    :return: The list of dictionaries corresponding to the rows to be displayed by tabulate.
    :rtype: list
    """
    # Check that the target_month is a valid month.
    try:
        _ = date(int(target_month[0:4]), int(target_month[5:7]), 1)
    except ValueError:
        raise ValueError("Invalid month.")

    income_row = {
        1: "Total Income",
        2: custom_format_amount(calculate_monthly_income(target_month)),
    }
    expense_row = {
        1: "Total Expense",
        2: custom_format_amount(calculate_monthly_expense(target_month)),
    }
    savings_row = {
        1: "Total Savings",
        2: custom_format_amount(calculate_monthly_savings(target_month)),
    }

    return [income_row, expense_row, savings_row]


def generate_monthly_top_expenses_by_category(
    target_month: str, max_number: int
) -> list[dict]:
    """
    Calculate the (up to) top max_number categories with highest total expense during the target month. Later to be displayed using tabulate using headers="keys".

    :param target_month: The target month in YYYY-MM format.
    :type target_month: str
    :param max_number: The maximum number of categories in the top.
    :type max_number: int

    :raise FileNotFoundError: If transactions file not found, or if settings.json not found.
    :raise ValueError: If target_month is not a valid month or is not given in the expected format, or if max_number is negative (could be useful to allow this, but currently isn't), or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount, or if settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If max_number is not an int, or if the values in settings.json are not of the expected type, or if amount is not a float.
    :return: The list of top expenses by category, as dictionaries with keys Category and Expense, and in descending order based on the amount in Expense.
    :rtype: list
    """
    try:
        _ = date(int(target_month[0:4]), int(target_month[5:7]), 1)
    except ValueError:
        raise ValueError("Invalid month.")

    if not isinstance(max_number, int):
        raise TypeError("max_number should be an int.")
    if max_number < 0:
        raise ValueError("max_number should be a non-negative int.")

    top_expenses = calculate_monthly_expense_by_category(target_month)[:max_number]
    formatted_top_expenses = [
        {
            "Category": dictionary["Category"].title(),
            "Expense": custom_format_amount(dictionary["Expense"]),
        }
        for dictionary in top_expenses
    ]

    return formatted_top_expenses


def generate_current_target_overview() -> list[dict]:
    """
    Create an overview of the current target savings, to be later displayed using tabulate.

    :raise FileNotFoundError: If transactions file not found, or if settings.json not found.
    :raise ValueError: If transactions file does not contain the expected headers, or if a transaction contains an invalid amount, or if settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type, or if amount is not a float.
    :return: The list of dictionaries corresponding to the rows to be displayed by tabulate.
    :rtype: list
    """
    target_savings_row = {
        1: "Target Monthly Savings",
        2: custom_format_amount(get_target_monthly_savings()),
    }
    current_target_daily_budget_row = {
        1: "Target Daily Budget",
        2: custom_format_amount(calculate_current_target_daily_budget()),
    }
    average_daily_expense_row = {
        1: "Average Daily Expense",
        2: custom_format_amount(calculate_average_daily_expense_current_month()),
    }
    expected_savings_row = {
        1: "Expected Monthly Savings",
        2: custom_format_amount(calculate_expected_savings_current_month()),
    }

    return [
        target_savings_row,
        current_target_daily_budget_row,
        average_daily_expense_row,
        expected_savings_row,
    ]


def generate_current_month_overview() -> list[dict]:
    """
    Create an overview of the current month, to be later displayed using tabulate.

    :raise FileNotFoundError: If transactions file not found, or if settings.json not found.
    :raise ValueError: If transactions file does not contain the expected headers, or if a transaction contains an invalid amount, or if settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type, or if amount is not a float.
    :return: The list of dictionaries corresponding to the rows to be displayed by tabulate.
    :rtype: list
    """
    current_month = date.today().isoformat()[0:7]
    income_row = {
        1: "Total Income",
        2: custom_format_amount(calculate_monthly_income(current_month)),
    }
    expense_row = {
        1: "Total Expense",
        2: custom_format_amount(calculate_monthly_expense(current_month)),
    }
    if date.today().isoformat()[8:10] != "01":
        rows = [income_row, expense_row] + generate_current_target_overview()
    else:
        rows = [income_row, expense_row] + generate_current_target_overview()[:2]

    return rows


# ==========================================
# SETTINGS HANDLERS
# ==========================================


def initialize_settings() -> None:
    """
    Creates default settings JSON file.

    :raise FileExistsError: If settings file already exists.
    :return: None
    :rtype: None
    """
    init_settings()


def get_settings() -> dict:
    """
    Retrieve the settings.

    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: The settings.
    :rtype: dict
    """
    return load_settings()


def get_locale() -> str:
    """
    Retrieve the locale from the settings.

    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: The locale.
    :rtype: str
    """
    settings = get_settings()
    return settings["locale"]


def set_locale(new_locale: str) -> None:
    """
    Update the locale in the settings.

    :param new_locale: The new locale, e.g., en_US.
    :type new_locale: str
    :raise FileNotFoundError: If settings.json not found.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If new_locale is not a string, or if the values in settings.json are not of the expected type.
    :raise ValueError: If new_locale is not a valid locale, or if settings.json exists but does not load into a dictionary.
    :return: None
    :rtype: None
    """
    settings = get_settings()

    if not isinstance(new_locale, str):
        raise TypeError("Locale should be specified as a string.")

    # Check that new_locale is a valid locale.
    if new_locale not in locale_identifiers():
        raise ValueError("Invalid new locale.")

    settings["locale"] = new_locale
    update_settings(settings)


def get_currency() -> str:
    """
    Retrieve the currency from the settings.

    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: The currency.
    :rtype: str
    """
    settings = get_settings()
    return settings["currency"]


def set_currency(new_currency: str) -> None:
    """
    Update the currency in the settings.

    :param new_currency: The new currency in ISO format.
    :type new_currency: str
    :raise FileNotFoundError: If settings.json not found.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If new_currency is not a string, or if the values in settings.json are not of the expected type.
    :raise ValueError: If new_currency is not a valid ISO format currency, or if settings.json exists but does not load into a dictionary.
    :return: None
    :rtype: None
    """
    settings = get_settings()

    if not isinstance(new_currency, str):
        raise TypeError("Currency should be given in ISO format as a string.")

    # Check that new_currency is a valid ISO currency.
    if new_currency not in list(get_global("all_currencies")):
        raise ValueError("Invalid new currency.")

    settings["currency"] = new_currency
    update_settings(settings)


def get_saved_categories() -> list:
    """
    Retrieve the saved categories from the settings.

    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: The list of saved categories.
    :rtype: list
    """
    settings = get_settings()
    return settings["saved_categories"]


def save_category(new_category: str) -> None:
    """
    Add a category to the list of saved categories in the settings.

    :param new_category: The new category, assumed already stripped and case-insensitive.
    :type new_category: str
    :raise FileNotFoundError: If settings.json not found.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the new category is not a string, or if the values in settings.json are not of the expected type.
    :raise ValueError: If the new category is already in the list of saved categories, or if settings.json exists but does not load into a dictionary.
    :return: None
    :rtype: None
    """
    saved_categories = get_saved_categories()

    if not isinstance(new_category, str):
        raise TypeError("New category should be a string.")

    if new_category.lower() in saved_categories:
        raise ValueError("Category already in the list of saved categories.")

    saved_categories.append(new_category.lower())
    saved_categories.sort()

    settings = get_settings()
    settings["saved_categories"] = saved_categories
    update_settings(settings)


def remove_category(target_category: str) -> None:
    """
    Remove the target category from the list of saved categories in the settings.

    :param target_category: The target category to be removed.
    :type target_category: str
    :raise FileNotFoundError: If settings.json not found.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :raise ValueError: If target category not in the list of saved categories, or if settings.json exists but does not load into a dictionary.
    :return: None
    :rtype: None
    """
    saved_categories = get_saved_categories()

    if target_category.lower() not in saved_categories:
        raise ValueError("Currently not in the list of saved categories.")

    settings = get_settings()
    settings["saved_categories"] = [
        category for category in saved_categories if category != target_category.lower()
    ]
    update_settings(settings)


def get_saved_monthly_transactions() -> list:
    """
    Retrieve the list of saved monthly transactions from the settings.

    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: The list of saved monthly transactions.
    :rtype: list
    """
    settings = get_settings()
    return settings["saved_monthly_transactions"]


def save_monthly_transaction(new_monthly_transaction: dict) -> None:
    """
    Add a new monthly transaction to the list of saved monthly transactions.

    :param new_monthly_transaction: The details of the new monthly transaction: Type (a string), Amount (a float), Category (a string) and Description (a string).
    :type new_monthly_transaction: dict
    :raise FileNotFoundError: If settings.json not found.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If new_monthly_transaction is not a dictionary, or if the values in settings.json are not of the expected type.
    :raise ValueError: If the new monthly transaction is already in the list of saved monthly transactions, or if type is not either expense or income, or if the amount is not a non-negative float, or if settings.json exists but does not load into a dictionary.
    :return: None
    :rtype: None
    """
    settings = get_settings()

    if not isinstance(new_monthly_transaction, dict):
        raise TypeError("New monthly transaction should be a dictionary.")

    required_keys = {
        "Type",
        "Amount",
        "Category",
        "Description",
    }
    if set(new_monthly_transaction.keys()) != required_keys:
        raise KeyError("Invalid monthly transaction keys.")

    for key in required_keys - {"Amount"}:
        if not isinstance(new_monthly_transaction[key], str):
            raise TypeError(f"{key} should be a string.")

    if new_monthly_transaction["Type"] not in ["expense", "income"]:
        raise ValueError("Type should be either expense or income.")

    if not isinstance(new_monthly_transaction["Amount"], float):
        raise TypeError("Amount should be a float.")

    if not new_monthly_transaction["Amount"] >= 0:
        raise ValueError("Amount should be a non-negative float.")

    if new_monthly_transaction in settings["saved_monthly_transactions"]:
        raise ValueError(
            "This monthly transaction is already in the list of saved monthly transactions."
        )

    settings["saved_monthly_transactions"].append(new_monthly_transaction)
    # Organize saved monthly transactions: first incomes, ordered by amount, and then expenses, ordered by amount.
    saved_monthly_incomes = [
        transaction
        for transaction in settings["saved_monthly_transactions"]
        if transaction["Type"] == "income"
    ]
    saved_monthly_expenses = [
        transaction
        for transaction in settings["saved_monthly_transactions"]
        if transaction["Type"] == "expense"
    ]
    settings["saved_monthly_transactions"] = sorted(
        saved_monthly_incomes, key=lambda x: x["Amount"], reverse=True
    ) + sorted(saved_monthly_expenses, key=lambda x: x["Amount"], reverse=True)

    update_settings(settings)


def remove_monthly_transaction(target_monthly_transaction: dict) -> None:
    """
    Remove the target monthly transaction from the list of saved monthly transactions.

    :param target_monthly_transaction: The monthly transaction to be removed.
    :type target_monthly_transaction: dict
    :raise FileNotFoundError: If settings.json not found.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :raise ValueError: If target monthly transaction is not on the list of saved monthly transactions, or if settings.json exists but does not load into a dictionary.
    :return: None
    :rtype: None
    """
    saved_monthly_transactions = get_saved_monthly_transactions()
    updated_saved_monthly_transactions = [
        transaction
        for transaction in saved_monthly_transactions
        if transaction != target_monthly_transaction
    ]

    if saved_monthly_transactions == updated_saved_monthly_transactions:
        raise ValueError(
            "Target monthly transaction is not on the list of saved monthly transactions."
        )

    settings = get_settings()
    settings["saved_monthly_transactions"] = updated_saved_monthly_transactions
    update_settings(settings)


# We do not need an update functionality for saved monthly transactions in settings, because they do not have associated IDs.


def get_target_monthly_savings() -> float:
    """
    Retrieve the target monthly savings from the settings.

    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: The target monthly savings.
    :rtype: float
    """
    settings = get_settings()
    return settings["target_monthly_savings"]


def set_target_monthly_savings(new_target_monthly_savings: float) -> None:
    """
    Update the target monthly settings in the settings.

    :param new_target_monthly_savings: The new target monthly savings.
    :type new_target_monthly_savings: float
    :raise FileNotFoundError: If settings.json not found.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the new target monthly savings is not a float, or if the values in settings.json are not of the expected type.
    :raise ValueError: If the new target monthly savings is negative or nan, or if settings.json exists but does not load into a dictionary.
    :return: None
    :rtype: None
    """
    settings = get_settings()

    if not isinstance(new_target_monthly_savings, float):
        raise TypeError("New target monthly savings should be a float.")

    if not new_target_monthly_savings >= 0:
        raise ValueError("New target monthly savings should be a non-negative float.")

    settings["target_monthly_savings"] = new_target_monthly_savings
    update_settings(settings)


def get_last_modified() -> str:
    """
    Retrieve the last modified date from the settings.

    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: The last modified date in YYYY-MM-DD format.
    :rtype: str
    """
    settings = get_settings()
    return settings["last_modified"]


# ==========================================
# SINGLE TRANSACTION HANDLERS
# ==========================================


def initialize_transactions() -> None:
    """
    Create the transactions.csv file.

    :raise FileExistsError: If transactions file already exists.
    :return: None
    :rtype: None
    """
    init_transactions()


def add_transaction(new_transaction: dict) -> None:
    """
    Add a new transaction.

    :param new_transaction: Dictionary containing the details of the new transaction. It should contain the following keys: Date, Type, Amount, Category, Frequency, Description. All of them should be strings, except for the Amount, which should be a float.
    :type new_transaction: dict
    :raise FileNotFoundError: If transactions file not found.
    :raise TypeError: If new_transaction is not a dictionary or if its values are not of the expected type.
    :raise KeyError: If the set of keys is not as expected.
    :raise ValueError: If the new transaction's date is not a valid date, or if the type is not either expense or income, or if the amount is not a non-negative float, or if the frequency is not either monthly or one-time.
    :return: None
    :rtype: None
    """
    if not isinstance(new_transaction, dict):
        raise TypeError("New transaction should be a dictionary.")

    required_keys = {
        "Date",
        "Type",
        "Amount",
        "Category",
        "Frequency",
        "Description",
    }
    if set(new_transaction.keys()) != required_keys:
        raise KeyError("Invalid transaction keys.")

    for key in required_keys - {"Amount"}:
        if not isinstance(new_transaction[key], str):
            raise TypeError(f"{key} in new_transaction should be a string.")

    # Check that the date is a valid date
    try:
        _ = date(
            int(new_transaction["Date"][0:4]),
            int(new_transaction["Date"][5:7]),
            int(new_transaction["Date"][8:10]),
        )
    except ValueError:
        raise ValueError("Invalid date.")

    if new_transaction["Type"] not in ["expense", "income"]:
        raise ValueError("Type should be either expense or income.")

    if not isinstance(new_transaction["Amount"], float):
        raise TypeError("Amount should be a float.")

    if not new_transaction["Amount"] >= 0:
        raise ValueError("Amount should be a non-negative float.")

    if new_transaction["Frequency"] not in ["monthly", "one-time"]:
        raise ValueError("Frequency should be either monthly or one-time.")

    # All necessary checks have been performed, and now we can call save_transaction from the data layer
    save_transaction(new_transaction)


def remove_transaction(target_id: str) -> None:
    """
    Remove the target transaction.

    :param target_id: The ID of the target transaction.
    :type target_id: str
    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :raise KeyError: If none or several transactions with the given ID are found.
    :return: None
    :rtype: None
    """
    delete_transaction(target_id)


def modify_transaction(target_id: str, target_key: str, new_value: str | float) -> None:
    """
    Modify the target value of the target transaction.

    :param target_id: The ID of the target transaction.
    :type target_id: str
    :param target_key: The key of the target value.
    :type target_key: str
    :param new_value: The new value.
    :type new_value: str or float
    :raise FileNotFoundError: If transactions file not found.
    :raise TypeError: If the new value is not of the correct type.
    :raise KeyError: If none or several transactions with the given ID are found, or if the target key is not a valid transaction key.
    :raise ValueError: If date is not a valid date, or if type is not expense or income, or if amount is not a non-negative float, or if the frequency is not monthly or one-time, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: None
    :rtype: None
    """
    if target_key == "Date":
        if not isinstance(new_value, str):
            raise TypeError("Date should be a string.")
        try:
            _ = date(int(new_value[0:4]), int(new_value[5:7]), int(new_value[8:10]))
        except ValueError:
            raise ValueError("Invalid date.")

    if target_key == "Type":
        if not isinstance(new_value, str):
            raise TypeError("Type should be a string.")
        if new_value not in ["expense", "income"]:
            raise ValueError("Type should be either expense or income.")

    if target_key == "Amount":
        if not isinstance(new_value, float):
            raise TypeError("Amount should be a float.")
        if not new_value >= 0:
            raise ValueError("Amount should be a non-negative float.")

    if target_key == "Frequency":
        if not isinstance(new_value, str):
            raise TypeError("Frequency should be a string.")
        if new_value not in ["monthly", "one-time"]:
            raise ValueError("Invalid frequency.")

    # All necessary checks have been performed, and now we can call update_transaction from the data layer
    update_transaction(target_id, target_key, new_value)


# ==========================================
# TRANSACTION LIST HANDLERS
# ==========================================


def get_transactions() -> list[dict]:
    """
    Retrieve list of transactions from transactions.csv.

    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: The list of transactions, each of them in a dictionary.
    :rtype: list
    """
    return load_transactions()


def filter_transactions(
    transaction_list: list[dict],
    target_id: str,
    target_date: str,
    target_type: str,
    minimum_amount: float,
    target_category: str,
    target_frequency: str,
    target_description: str,
) -> list[dict]:
    """
    Filters input transaction_list by ID, Date, Type, Amount, Category, Frequency or Description. With respect to the Amount, the function returns all the transactions whose Amount is at least the given amount. With respect to the other properties, it returns all the transactions whose values match the target strings. The string arguments can be regular expressions.

    :param transaction_list: The list of dictionaries to filter, each dictionary representing a transaction.
    :type transaction_list: list
    :param target_id: The desired ID.
    :type target_id: str
    :param target_date: The desired date in YYYY-MM-DD format.
    :type target_date: str
    :param target_type: The desired type: expense or income.
    :type target_type: str
    :param minimum_amount: The desired minimum amount; only transactions of at least that amount will be in the output.
    :type minimum_amount: float
    :param target_category: The desired category.
    :type target_category: str
    :param target_frequency: The desired frequency: monthly or one-time.
    :type target_frequency: str
    :param target_description: The desired description.
    :type target_description: str
    :raise TypeError: If transaction_list is not a list, or if its entries are not dictionaries.
    :raise ValueError: If the arguments contain invalid regular expressions.
    :return: The filtered list of transactions.
    :rtype: list
    """
    if not isinstance(transaction_list, list):
        raise TypeError("The input should be a list of transactions.")

    if not all(isinstance(item, dict) for item in transaction_list):
        raise TypeError("The transactions in the input list should be dictionaries.")

    # We intentionally do not check that the target_type is either expense or income, or that the target_frequency is either monthly or one-time, etc. It might be useful for the future or for debugging to allow to search for different values in those fields.

    try:
        relevant_transactions = [
            transaction
            for transaction in transaction_list
            if re.search(target_id, transaction["ID"])
            and re.search(target_date, transaction["Date"])
            and re.search(target_type, transaction["Type"])
            and transaction["Amount"] >= minimum_amount
            and re.search(target_category, transaction["Category"])
            and re.search(target_frequency, transaction["Frequency"])
            and re.search(target_description, transaction["Description"])
        ]
    except re.error:
        raise ValueError("Invalid regular expression.")
    return relevant_transactions


# Allowing for earliest date in the previous filtering function seems inefficient, so instead we define the function filter_transactions_between_dates below.


def filter_transactions_between_dates(
    transaction_list: list[dict], first_date: str, last_date: str
) -> list[dict]:
    """
    Filters the input list of transactions returning the sublist of those transactions whose Date is at least first_date and at most last_date, both included.

    :param transaction_list: The list of transactions to filter.
    :type transaction_list: list
    :param first_date: The first date in YYYY-MM-DD format.
    :type first_date: str
    :param last_date: The last date in YYYY-MM-DD format.
    :type last_date: str
    :raise TypeError: If first_date or last_date is not a string, or if transaction_list is not a list, or if its entries are not dictionaries.
    :raise ValueError: If first_date or last_date are not valid dates.
    :return: The sublist of transactions between the two dates.
    :rtype: list
    """
    if not isinstance(transaction_list, list):
        raise TypeError("The input should be a list of transactions.")

    if not all(isinstance(item, dict) for item in transaction_list):
        raise TypeError("The transactions in the input list should be dictionaries.")

    if not isinstance(first_date, str):
        raise TypeError("First date should be a string.")
    if not isinstance(last_date, str):
        raise TypeError("Last date should be a string.")
    try:
        date_0 = date(int(first_date[0:4]), int(first_date[5:7]), int(first_date[8:10]))
    except ValueError:
        raise ValueError("Invalid first date.")
    try:
        date_1 = date(int(last_date[0:4]), int(last_date[5:7]), int(last_date[8:10]))
    except ValueError:
        raise ValueError("Invalid last date.")

    try:
        relevant_transactions = [
            transaction
            for transaction in transaction_list
            if date_0
            <= date(
                int(transaction["Date"][0:4]),
                int(transaction["Date"][5:7]),
                int(transaction["Date"][8:10]),
            )
            <= date_1
        ]
    except ValueError:
        raise ValueError("Invalid date in the list of transactions.")

    return relevant_transactions


def sort_transactions(transaction_list: list[dict], key_list: list[str]) -> list[dict]:
    """
    Sort the input list of transaction "lexicographically" with respect to the list of keys. If key_list is the empty list, it just orders the transactions by (Date, ID). Both date and ID are ordered from lower to higher.

    :param transaction_list: The transactions to sort.
    :type transaction_list: list
    :param key_list: The list of keys to use to sort the transactions.
    :type key_list: list
    :raise TypeError: If key_list is not a list, or if its values are not strings, or if transaction_list is not a list, or if its entries are not dictionaries.
    :raise KeyError: If the keys do not correspond to a valid set of keys.
    :raise ValueError: If key list contains repetitions.
    :return: The list of transactions sorted according to the list of keys.
    :rtype: list
    """
    if not isinstance(transaction_list, list):
        raise TypeError("The input should be a list of transactions.")

    if not all(isinstance(item, dict) for item in transaction_list):
        raise TypeError("The transactions in the input list should be dictionaries.")

    if not isinstance(key_list, list) or not all(
        isinstance(item, str) for item in key_list
    ):
        raise TypeError("Key list should be a list of strings.")

    key_list = [item.title() for item in key_list]
    valid_keys = {
        "Date",
        "Type",
        "Amount",
        "Category",
        "Frequency",
        "Description",
    }
    if not all(item in valid_keys for item in key_list):
        raise KeyError("Keys do not correspond to a valid set of keys.")

    # Make sure that key_list has no repetitions.
    if len(key_list) != len(set(key_list)):
        raise ValueError("List of keys contains repetitions.")

    # Amounts should be ordered in descending order, so we split the key list in up three (possibly empty) sublists to sort in three stages.
    final_stage_keys = key_list
    first_stage_keys = []
    for i in range(len(key_list)):
        if key_list[i].title() == "Amount":
            final_stage_keys = key_list[:i]
            first_stage_keys = key_list[(i + 1) :]

    sorted_transactions = sorted(
        transaction_list,
        key=lambda x: int(x["ID"]),
    )
    sorted_transactions = sorted(
        sorted_transactions,
        key=lambda x: x["Date"],
    )
    sorted_transactions = sorted(
        sorted_transactions, key=lambda x: tuple(x[key] for key in first_stage_keys)
    )
    if "Amount" in key_list:
        sorted_transactions = sorted(
            sorted_transactions, key=lambda x: x["Amount"], reverse=True
        )
    sorted_transactions = sorted(
        sorted_transactions, key=lambda x: tuple(x[key] for key in final_stage_keys)
    )

    return sorted_transactions


# ==========================================
# GENERAL ARITHMETIC FUNCTIONS
# ==========================================


def calculate_total_amount(transaction_list: list[dict]) -> float:
    """
    Calculate the sum of the amounts of the transactions in the input transactions list.

    :param transaction_list: The list of transactions whose total amount we want to calculate.
    :type transaction_list: list
    :raise TypeError: If transaction_list is not a list, or if its entries are not dictionaries, or if the Amount of one of the dictionaries is not a float.
    :raise KeyError: If a dictionary on the list does not have an Amount key.
    :return: The sum of the amounts, possibly nan.
    :rtype: float
    """
    if not isinstance(transaction_list, list):
        raise TypeError("The input should be a list of transactions.")

    if not all(isinstance(item, dict) for item in transaction_list):
        raise TypeError("The transactions in the input list should be dictionaries.")

    if not all("Amount" in item.keys() for item in transaction_list):
        raise KeyError(
            "All transactions in the transactions list should have an Amount key."
        )

    total_amount = 0.0
    for transaction in transaction_list:
        total_amount += transaction["Amount"]

    return total_amount


def calculate_average_daily_amount_between_dates(
    transaction_list: list[dict], first_date: str, last_date: str
) -> float:
    """
    Calculates the average daily amount between first_date and last_date, both included. Last date should not be earlier than first date.

    :param transaction_list: The list of transactions whose daily average amount we want to calculate.
    :type transaction_list: list
    :param first_date: The first date in format YYYY-MM-DD.
    :type first_date: str
    :param last_date: The second date in format YYYY-MM-DD.
    :type last_date: str
    :raise TypeError: If first_date or last_date is not a string, or if transaction_list is not a list, or if its entries are not dictionaries, or if the Amount of one of the dictionaries is not a float.
    :raise KeyError: If a dictionary on the list does not have an Amount key.
    :raise ValueError: If first_date or last_date are not valid dates, or if last_date is earlier than first_date.
    :return: The average daily amount between these dates.
    :rtype: float
    """
    if not isinstance(first_date, str):
        raise TypeError("First date should be a string.")
    if not isinstance(last_date, str):
        raise TypeError("Last date should be a string.")
    try:
        date_0 = date(int(first_date[0:4]), int(first_date[5:7]), int(first_date[8:10]))
    except ValueError:
        raise ValueError("Invalid first date.")
    try:
        date_1 = date(int(last_date[0:4]), int(last_date[5:7]), int(last_date[8:10]))
    except ValueError:
        raise ValueError("Invalid last date.")
    if date_1 < date_0:
        raise ValueError("Last date is earlier than first date.")

    relevant_transactions = filter_transactions_between_dates(
        transaction_list, first_date, last_date
    )
    total_amount = calculate_total_amount(relevant_transactions)
    total_days = (date_1 - date_0).days + 1

    # We intentionally do not round the result to two decimal places.
    return total_amount / total_days


# ==========================================
# MONTHLY FUNCTIONS
# ==========================================


def add_monthly_transactions(target_month: str) -> None:
    """
    Adds the saved monthly transactions to the target month, all of them with date the first day of the target month.

    :param target_month: The target month in YYYY-MM format.
    :type target_month: str
    :raise FileNotFoundError: If settings.json not found, or if transactions file not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount, or if target_month is not a valid month or is not given in the expected format, or if target month already contains some monthly transactions.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: None
    :rtype: None
    """
    try:
        _ = date(int(target_month[0:4]), int(target_month[5:7]), 1)
    except ValueError:
        raise ValueError("Invalid month.")

    first_of_target_month = target_month + "-01"

    saved_monthly_transactions = get_saved_monthly_transactions()
    target_month_monthly_transactions = filter_transactions(
        get_transactions(), ".*", f"{target_month}-..", ".*", 0.0, ".*", "monthly", ".*"
    )
    if len(target_month_monthly_transactions) > 0:
        raise ValueError("Target month already contains some monthly transactions.")
    for transaction in saved_monthly_transactions:
        new_transaction = {
            "Date": first_of_target_month,
            "Type": transaction["Type"],
            "Amount": transaction["Amount"],
            "Category": transaction["Category"],
            "Frequency": "monthly",
            "Description": transaction["Description"],
        }
        add_transaction(new_transaction)


def calculate_monthly_total(
    target_month: str,
    target_type: str,
    target_category: str,
    target_frequency: str,
    target_description: str,
) -> float:
    """
    Calculate the monthly total of the target type of transaction. The string arguments can be regular expressions.

    :param target_month: The target month in YYYY-MM format.
    :type target_month: str
    :param target_type: The target type: expense or income.
    :type target_type: str
    :param target_category: The target category.
    :type target_category: str
    :param target_frequency: The target frequency: monthly or one-time.
    :type target_frequency: str
    :param target_description: The target description.
    :type target_description: str
    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If target_month is not a valid month or is not given in the expected format, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount, or if the arguments contain invalid regular expressions.
    :return: The total monthly expense.
    :rtype: float
    """
    try:
        _ = date(int(target_month[0:4]), int(target_month[5:7]), 1)
    except ValueError:
        raise ValueError("Invalid month.")

    # As in filter_transactions, we intentionally do not limit the possibilities for target_type and target_frequency.

    transactions = get_transactions()
    target_transactions = filter_transactions(
        transactions,
        ".*",
        f"{target_month}-..",
        target_type,
        0.0,
        target_category,
        target_frequency,
        target_description,
    )
    return calculate_total_amount(target_transactions)


def calculate_monthly_income(target_month: str) -> float:
    """
    Calculate the total income of the target month.

    :param target_month: The target month in YYYY-MM format.
    :type target_month: str
    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If target_month is not a valid month or is not given in the expected format, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: The total income of the target month.
    :rtype: float
    """
    try:
        _ = date(int(target_month[0:4]), int(target_month[5:7]), 1)
    except ValueError:
        raise ValueError("Invalid month.")

    return calculate_monthly_total(target_month, "income", ".*", ".*", ".*")


def calculate_monthly_expense(target_month: str) -> float:
    """
    Calculate the total expense of the target month.

    :param target_month: The target month in YYYY-MM format.
    :type target_month: str
    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If target_month is not a valid month or is not given in the expected format, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: The total expense of the target month.
    :rtype: float
    """
    try:
        _ = date(int(target_month[0:4]), int(target_month[5:7]), 1)
    except ValueError:
        raise ValueError("Invalid month.")

    return calculate_monthly_total(target_month, "expense", ".*", ".*", ".*")


def calculate_monthly_fixed_expense(target_month: str) -> float:
    """
    Calculate the total fixed expense of the target month.

    :param target_month: The target month in YYYY-MM format.
    :type target_month: str
    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If target_month is not a valid month or is not given in the expected format, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: The total fixed expense of the target month.
    :rtype: float
    """
    try:
        _ = date(int(target_month[0:4]), int(target_month[5:7]), 1)
    except ValueError:
        raise ValueError("Invalid month.")

    return calculate_monthly_total(target_month, "expense", ".*", "monthly", ".*")


def calculate_monthly_variable_expense(target_month: str) -> float:
    """
    Calculate the total variable expense of the target month.

    :param target_month: The target month in YYYY-MM format.
    :type target_month: str
    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If target_month is not a valid month or is not given in the expected format, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: The total variable expense of the target month.
    :rtype: float
    """
    try:
        _ = date(int(target_month[0:4]), int(target_month[5:7]), 1)
    except ValueError:
        raise ValueError("Invalid month.")

    return calculate_monthly_total(target_month, "expense", ".*", "one-time", ".*")


def calculate_monthly_savings(target_month: str) -> float:
    """
    Calculate the total savings of the target month.

    :param target_month: The target month in YYYY-MM format.
    :type target_month: str
    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If target_month is not a valid month or is not given in the expected format, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: The total savings of the target month.
    :rtype: float
    """
    try:
        _ = date(int(target_month[0:4]), int(target_month[5:7]), 1)
    except ValueError:
        raise ValueError("Invalid month.")

    return calculate_monthly_income(target_month) - calculate_monthly_expense(
        target_month
    )


def calculate_monthly_expense_by_category(target_month: str) -> list[dict]:
    """
    Calculate the total expense of the target month category by category. The output is given as a list of dictionaries, sorted by amount.

    :param target_month: The target month in YYYY-MM format.
    :type target_month: str
    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If target_month is not a valid month or is not given in the expected format, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: A list of dictionaries with keys Category and Expense and with corresponding values, sorted by amount.
    :rtype: list
    """
    try:
        _ = date(int(target_month[0:4]), int(target_month[5:7]), 1)
    except ValueError:
        raise ValueError("Invalid month.")

    transactions = get_transactions()
    relevant_transactions = filter_transactions(
        transactions, ".*", f"{target_month}-..", "expense", 0.0, ".*", ".*", ".*"
    )
    relevant_categories = get_categories_from_transactions(relevant_transactions)
    expense_by_category = []
    for category in relevant_categories:
        # We use re.escape(category), in case the category contains special characters such as *.
        expense_by_category.append(
            {
                "Category": category,
                "Expense": calculate_monthly_total(
                    target_month, "expense", f"^{re.escape(category)}$", ".*", ".*"
                ),
            }
        )
    return sorted(expense_by_category, key=lambda x: x["Expense"], reverse=True)


# ==========================================
# CURRENT MONTH FUNCTIONS
# ==========================================


def calculate_budget_current_month() -> float:
    """
    Calculate the budget for the current month.

    :raise FileNotFoundError: If settings.json not found, or if transactions file not found.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :raise ValueError: If settings.json contains invalid keys or is missing required keys, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: The budget for the current month.
    :rtype: float
    """
    current_month = date.today().isoformat()[0:7]
    income_current_month = calculate_monthly_income(current_month)
    fixed_expense_current_month = calculate_monthly_fixed_expense(current_month)
    target_savings = get_target_monthly_savings()

    return income_current_month - fixed_expense_current_month - target_savings


def calculate_remaining_budget_current_month() -> float:
    """
    Calculate the remaining budget for the current month.

    :raise FileNotFoundError: If settings.json not found, or if transactions file not found.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :raise ValueError: If settings.json contains invalid keys or is missing required keys, or if transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: The remaining budget for the current month.
    :rtype: float
    """
    current_month = date.today().isoformat()[0:7]
    income_current_month = calculate_monthly_income(current_month)
    expense_current_month = calculate_monthly_expense(current_month)
    target_savings = get_target_monthly_savings()

    return income_current_month - expense_current_month - target_savings


def calculate_average_daily_expense_current_month() -> float:
    """
    Calculate the average daily expense during the current month until yesterday included. In particular, it does not take the current day of the month into account. Returns nan if today is the first day of the month.

    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: The average daily expense until yesterday included.
    :rtype: float
    """
    today = date.today()
    daily_expenses = filter_transactions(
        get_transactions(), ".*", ".*", "expense", 0.0, ".*", "one-time", ".*"
    )
    if today.day == 1:
        average_daily_expense = float("nan")
    else:
        yesterday = today.replace(day=today.day - 1)
        first_of_month = today.replace(day=1)
        average_daily_expense = calculate_average_daily_amount_between_dates(
            daily_expenses, first_of_month.isoformat(), yesterday.isoformat()
        )

    return average_daily_expense


def calculate_expected_savings_current_month() -> float:
    """
    Calculate the expected savings for the current month, based on the average daily expense during the current month until yesterday included. In particular, it does not take the current day of the month into account. Returns nan if today is the first day of the month.

    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: The expected savings.
    :rtype: float
    """
    today = date.today()
    # Calculate remaining days including today:
    first_day_next_month = get_first_day_next_month(today)
    remaining_days_current_month = (first_day_next_month - today).days
    current_month = today.isoformat()[0:7]
    fixed_expense_current_month = calculate_monthly_fixed_expense(current_month)
    expected_expense = (
        fixed_expense_current_month
        + calculate_average_daily_expense_current_month() * remaining_days_current_month
    )
    income_current_month = calculate_monthly_income(current_month)

    return income_current_month - expected_expense


def calculate_current_target_daily_budget() -> float:
    """
    Calculate the current target daily budget, taking the current average daily expense into account. It does not take the current day's expense into account.

    :raise FileNotFoundError: If transactions file not found.
    :raise ValueError: If transactions file does not contain the expected headers, or if a transaction contains an invalid amount.
    :return: The current target daily budget.
    :rtype: float
    """
    today = date.today()
    first_of_month = today.replace(day=1)

    current_month = today.isoformat()[0:7]
    fixed_expense_current_month = calculate_monthly_fixed_expense(current_month)

    first_of_month = today.replace(day=1)
    if today == first_of_month:
        total_daily_expense_until_yesterday = 0.0
    else:
        total_daily_expense_until_yesterday = (
            today - first_of_month
        ).days * calculate_average_daily_expense_current_month()
    first_day_next_month = get_first_day_next_month(today)
    remaining_days_current_month = (first_day_next_month - today).days

    income_current_month = calculate_monthly_income(current_month)
    remaining_budget_yesterday = (
        income_current_month
        - get_target_monthly_savings()
        - fixed_expense_current_month
        - total_daily_expense_until_yesterday
    )

    return remaining_budget_yesterday / remaining_days_current_month


# ==========================================
# FORMATTING FUNCTIONS
# ==========================================


def custom_format_amount(amount: float) -> str:
    """
    Format the input amount according to the locale in settings.json.

    :param amount: The amount to be formatted.
    :type amount: float
    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type, or if amount is not a float.
    :return: The formatted amount.
    :rtype: str
    """
    if not isinstance(amount, float):
        raise TypeError("Amount should be a float.")
    return format_currency(
        round(amount, 2), currency=get_currency(), locale=get_locale()
    ).replace("\xa0", " ")


def custom_format_date(target_date: str) -> str:
    """
    Format the target date according to the locale in settings.json.

    :param target_date: The target date in YYYY-MM-DD format.
    :type target_date: str
    :raise FileNotFoundError: If settings.json not found.
    :raise ValueError: If settings.json exists but does not load into a dictionary, or if the date is not a valid date given in the expected format.
    :raise KeyError: If settings.json contains invalid keys or is missing required keys.
    :raise TypeError: If the values in settings.json are not of the expected type.
    :return: The formatted date.
    :rtype: str
    """
    try:
        target_date_object = date.fromisoformat(target_date)
    except ValueError:
        raise ValueError("Invalid date.")
    return format_date(target_date_object, format="short", locale=get_locale())


def format_transaction(transaction: dict, header_list: list[str]) -> dict:
    """
    Format the input transaction according to header_list.

    :param transaction: The transaction to format.
    :type transaction: dict
    :param header_list: The list of headers to use as a blueprint to format the transaction.
    :type header_list: list
    :raise FileNotFoundError: If settings.json not found.
    :raise TypeError: If header_list is not a list or if its values are not strings, or if the values in settings.json are not of the expected type.
    :raise KeyError: If the headers do not correspond to a valid set of keys, or if settings.json contains invalid keys or is missing required keys.
    :raise ValueError: If header list contains repetitions, or if settings.json exists but does not load into a dictionary.
    :return: The transaction formatted according to the list of headers.
    :rtype: dict
    """
    if not isinstance(header_list, list) or not all(
        isinstance(item, str) for item in header_list
    ):
        raise TypeError("Header list should be a list of strings.")

    valid_keys = {
        "Date",
        "Type",
        "Amount",
        "Category",
        "Frequency",
        "Description",
    }
    if not all(item.title() in valid_keys for item in header_list):
        raise KeyError("Headers do not correspond to a valid set of keys.")

    # Make sure that header_list has no repetitions.
    if len(header_list) != len(set([item.title() for item in header_list])):
        raise ValueError("List of headers contains repetitions.")

    # First format the whole transaction.
    formatted_transaction = transaction.copy()
    formatted_transaction["Date"] = custom_format_date(formatted_transaction["Date"])
    formatted_transaction["Type"] = formatted_transaction["Type"].title()
    formatted_transaction["Amount"] = custom_format_amount(
        formatted_transaction["Amount"]
    )
    formatted_transaction["Category"] = formatted_transaction["Category"].title()
    formatted_transaction["Frequency"] = formatted_transaction["Frequency"].title()

    # Then filter and rearrange its keys according to the headers list.
    formatted_transaction = {
        key: formatted_transaction[key.title()] for key in header_list
    }

    return formatted_transaction


# ==========================================
# OTHER AUXILIARY FUNCTIONS
# ==========================================


def get_categories_from_transactions(transaction_list: list) -> list:
    """
    Retrieve the categories that appear in the input list of transactions.

    :param transaction_list: The target list of transactions.
    :type transaction_list: list
    :return: The list of categories that appear in the target list of transactions.
    :rtype: list
    """
    relevant_categories = set()
    for transaction in transaction_list:
        relevant_categories.add(transaction["Category"])
    return sorted(relevant_categories)


def get_first_day_next_month(target_date: date) -> date:
    """
    Returns the first day of the next month to target_date.

    :param target_date: The date for which we want to calculate the first day of the next month.
    :type target_date: date
    :return: The first day of the next month.
    :rtype: date
    """
    if target_date.month != 12:
        return target_date.replace(month=target_date.month + 1, day=1)
    else:
        return target_date.replace(year=target_date.year + 1, month=1, day=1)


"""UI LAYER

UI code:
- Prompt functions.
- Display functions.
- Raw user-input validation.
"""

# ==========================================
# PROMPT FUNCTIONS
# ==========================================


def prompt_main_menu() -> str:
    """
    Prompt user to choose an option from the main menu.

    :return: The chosen option.
    :rtype: str
    """
    display_main_menu()
    while True:
        user_input = input("Enter a number 0-10: ").strip()
        if user_input in [f"{i}" for i in range(11)]:
            chosen_option = user_input
            break
        else:
            print("Invalid input.")
            continue
    return chosen_option


def prompt_date() -> str:
    """
    Prompt user to specify the date of a transaction.

    :return: The chosen date in YYYY-MM-DD format.
    :rtype: str
    """
    while True:
        user_input = input("Date [YYYY-MM-DD]: ").strip()
        try:
            chosen_date = date.fromisoformat(user_input).isoformat()
            break
        except ValueError:
            print("Invalid input. Enter a valid date in YYYY-MM-DD format.")
    return chosen_date


def prompt_type() -> str:
    """
    Prompt user to specify the type of a transaction.

    :return: The chosen type, either expense or income.
    :rtype: str
    """
    while True:
        user_input = input("Type [expense/income]: ").strip().lower()
        if user_input in ["expense", "income"]:
            chosen_type = user_input
            break
        else:
            print("Invalid input. Enter either expense or income.")
            continue
    return chosen_type


def prompt_amount() -> float:
    """
    Prompt user to specify the amount of a transaction.

    :return: The chosen amount.
    :rtype: float
    """
    while True:
        user_input = input("Amount [non-negative float]: ").strip()
        try:
            chosen_amount = float(user_input)
            if chosen_amount >= 0:
                break
            else:
                print("Invalid input. Enter a non-negative float.")
        except ValueError:
            print("Invalid input. Enter a non-negative float.")
    return chosen_amount


def prompt_category() -> str:
    """
    Prompt user to specify a category.

    :return: The chosen category.
    :rtype: str
    """
    if len(get_saved_categories()) == 0:
        while True:
            user_input = input("Enter a category: ").strip().lower()
            if user_input == "":
                print("Invalid input: Category must be non-empty.")
                continue
            elif user_input.isdigit():
                print("Invalid input: Category cannot be a number.")
                continue
            else:
                chosen_category = user_input
                prompt_save_category(chosen_category)
                break
    else:
        display_saved_categories()
        while True:
            user_input = input("Select or enter a category: ").strip().lower()
            if user_input == "":
                print("Invalid input: Category must be non-empty.")
                continue
            elif user_input == "-1":
                print(
                    f"Invalid input. Select a category 0-{len(get_saved_categories())-1} or enter a category directly."
                )
                continue
            index = -1
            try:
                index = int(user_input)
            except ValueError:
                pass
            if index == -1:
                # User has typed the category directly.
                chosen_category = user_input.lower()
                if chosen_category not in get_saved_categories():
                    prompt_save_category(chosen_category)
                break
            elif 0 <= index < len(get_saved_categories()):
                chosen_category = get_saved_categories()[index]
                break
            else:
                print(
                    f"Invalid input. Select a category 0-{len(get_saved_categories())-1} or enter a category directly."
                )
    return chosen_category


def prompt_save_category(target_category: str) -> None:
    """
    Prompt user to add category in the list of saved categories.

    :param target_category: The target category.
    :type target_category: str
    :return: None
    :rtype: None
    """
    while True:
        match input("Add category to the list of saved categories? [y/n] ").strip():
            case "y":
                save_category(target_category)
                print("Category added.")
                break
            case "n":
                break
            case _:
                print("Invalid input. Enter y or n.")


def prompt_frequency() -> None:
    """
    Prompt user to specify the frequency of a transaction.

    :return: The chosen frequency, either one-time or monthly.
    :rtype: str
    """
    while True:
        user_input = input("Frequency [one-time/monthly]: ").strip().lower()
        if user_input in ["one-time", "monthly"]:
            chosen_frequency = user_input
            break
        else:
            print("Invalid input. Enter either one-time or monthly.")
            continue
    return chosen_frequency


def prompt_save_monthly_transaction(target_transaction: dict) -> None:
    """
    Prompt user to save the input transaction in the list of saved monthly transactions.

    :param target_transaction: The target transaction.
    :type target_transaction: dict
    :return: None
    :rtype: None
    """
    while True:
        match input(
            "Add transaction to the list of saved monthly transactions? [y/n] "
        ).strip():
            case "y":
                new_monthly_transaction = target_transaction.copy()
                try:
                    del new_monthly_transaction["ID"]
                except KeyError:
                    pass
                try:
                    del new_monthly_transaction["Date"]
                except KeyError:
                    pass
                try:
                    del new_monthly_transaction["Frequency"]
                except KeyError:
                    pass
                save_monthly_transaction(new_monthly_transaction)
                print("Transaction added to the list of saved monthly transactions.")
                break
            case "n":
                break
            case _:
                print("Invalid input. Enter y or n.")


def prompt_add_onetime_expense() -> None:
    """
    Prompt user to add a one-time expense with date the current date.

    :return: None
    :rtype: None
    """
    new_expense = {
        "Date": date.today().isoformat(),
        "Type": "expense",
        "Amount": prompt_amount(),
        "Category": prompt_category(),
        "Frequency": "one-time",
        "Description": input("Description: ").strip(),
    }
    add_transaction(new_expense)
    print("Expense added.")


def prompt_add_transaction() -> None:
    """
    Prompt user to add a transaction.

    :return: None
    :rtype: None
    """
    new_transaction = {
        "Date": prompt_date(),
        "Type": prompt_type(),
        "Amount": prompt_amount(),
        "Category": prompt_category(),
        "Frequency": prompt_frequency(),
        "Description": input("Description: ").strip(),
    }
    if new_transaction["Frequency"] == "monthly":
        prompt_save_monthly_transaction(new_transaction)
    add_transaction(new_transaction)
    print("Transaction added.")


def prompt_get_transaction_by_date() -> str:
    """
    Prompt the user to select a transaction by date, and return the target transaction's ID. Regular expressions are allowed.

    :return: The target transaction's ID, or None if no transaction was selected.
    :rtype: str
    """
    while True:
        transaction_date = input("Transaction's date in YYYY-MM-DD format: ").strip()
        try:
            relevant_transactions = filter_transactions(
                get_transactions(),
                ".*",
                "^" + transaction_date + "$",
                ".*",
                0.0,
                ".*",
                ".*",
                ".*",
            )
        except ValueError:
            print("Error: Invalid regular expression.")
            continue
        if len(relevant_transactions) == 0:
            print("No transactions on that date.")
            continue
        else:
            display_transactions(relevant_transactions)
            while True:
                user_input = input("Select a transaction: ").strip()
                try:
                    index = int(user_input)
                    return relevant_transactions[index]["ID"]
                except (ValueError, IndexError):
                    print(
                        f"Invalid input. Select a transaction 0-{len(relevant_transactions)-1}."
                    )
                    continue


def prompt_modify_transaction() -> None:
    """
    Prompt user to modify a transaction.

    :return: None
    :rtype: None
    """
    target_id = prompt_get_transaction_by_date()
    relevant_transaction = filter_transactions(
        get_transactions(),
        target_id,
        ".*",
        ".*",
        0.0,
        ".*",
        ".*",
        ".*",
    )[0]
    while True:
        target_key = (
            input("Key [Date/Type/Amount/Category/Frequency/Description]: ")
            .strip()
            .title()
        )
        if target_key in [
            "Date",
            "Type",
            "Amount",
            "Category",
            "Frequency",
            "Description",
        ]:
            break
        else:
            print(
                "Invalid input. Enter a valid key: Date, Type, Amount, Category, Frequency or Description."
            )
            continue
    match target_key:
        case "Date":
            new_value = prompt_date()
        case "Type":
            new_value = prompt_type()
        case "Amount":
            new_value = prompt_amount()
        case "Category":
            new_value = prompt_category()
        case "Frequency":
            new_value = prompt_frequency()
        case "Description":
            new_value = input("Description: ").strip()
    if new_value == relevant_transaction[target_key]:
        print(f"The new {target_key.lower()} is the same as the old one.")
    else:
        modify_transaction(target_id, target_key, new_value)
        print("Transaction modified.")


def prompt_delete_transaction() -> None:
    """
    Prompt user to delete a transaction.

    :return: None
    :rtype: None
    """
    target_id = prompt_get_transaction_by_date()
    remove_transaction(target_id)
    print("Transaction deleted.")


def prompt_month_summary() -> None:
    """
    Prompt the user to select a month and display the corresponding month summary.

    :return: None
    :rtype: None
    """
    while True:
        target_month = input("Month [YYYY-MM]: ").strip()
        try:
            _ = date.fromisoformat(target_month + "-01")
            break
        except ValueError:
            print("Invalid input. Enter a valid month in YYYY-MM format.")
            continue
    transactions_target_month = filter_transactions(
        get_transactions(),
        ".*",
        f"{target_month}-..",
        ".*",
        0.0,
        ".*",
        ".*",
        ".*",
    )
    if len(transactions_target_month) == 0:
        print("No transactions during that month.")
    else:
        display_month_summary(target_month)


def prompt_search_transactions() -> None:
    """
    Prompt the user to search transactions and display the resulting list of transactions. Regular expressions are allowed.

    :return: None
    :rtype: None
    """
    target_date = input("Date [YYYY-MM-DD]: ")
    target_type = input("Type [expense/income]: ")
    while True:
        user_input = input("Minimum amount [float]: ").strip()
        if user_input == "":
            minimum_amount = 0.0
            break
        try:
            minimum_amount = float(user_input)
            break
        except ValueError:
            print("Invalid minimum amount. Please enter a float or leave empty.")
            continue
    target_category = input("Category: ")
    target_frequency = input("Frequency [one-time/monthly]: ")
    target_description = input("Description: ")
    try:
        relevant_transactions = filter_transactions(
            get_transactions(),
            ".*",
            target_date,
            target_type,
            minimum_amount,
            target_category,
            target_frequency,
            target_description,
        )
        display_transactions(relevant_transactions)
        print()
        print()
        input("[Press Enter to go back to the Main Menu] ")
    except ValueError:
        print("Error: Invalid regular expression.")


def prompt_settings_menu() -> str:
    """
    Prompt user to choose an option from the settings menu.

    :return: The chosen option.
    :rtype: str
    """
    display_settings_menu()
    while True:
        user_input = input("Enter a number 0-8: ").strip()
        if user_input in [f"{i}" for i in range(9)]:
            chosen_option = user_input
            break
        else:
            print("Invalid input.")
            continue
    return chosen_option


def prompt_locale() -> None:
    """
    Prompt user to specify a new locale.

    :return: None
    :rtype: None
    """
    while True:
        try:
            set_locale(input("Locale [e.g. en_US]: ").strip())
            print("Locale set to " + get_locale())
            break
        except ValueError:
            print("Invalid locale.")
            continue


def prompt_currency() -> None:
    """
    Prompt user to specify a new currency.

    :return: None
    :rtype: None
    """
    while True:
        try:
            set_currency(input("Currency [ISO format, e.g. USD]: ").strip())
            print("Currency set to " + get_currency())
            break
        except ValueError:
            print("Invalid currency.")
            continue


def prompt_add_category() -> None:
    """
    Prompt user to add a category to the list of saved categories.

    :return: None
    :rtype: None
    """
    while True:
        new_category = input("Category: ").strip()
        try:
            save_category(new_category)
            print(new_category.title() + " added to the list of saved categories.")
            break
        except ValueError:
            print("Category already in the list of saved categories.")
            break


def prompt_delete_category() -> None:
    """
    Prompt user to delete a category from the list of saved categories.

    :return: None
    :rtype: None
    """
    saved_categories = get_saved_categories()
    if len(saved_categories) == 0:
        print("The list of saved categories is empty.")
    else:
        display_saved_categories()
        while True:
            user_input = input("Select a category: ").strip()
            if user_input in [f"{i}" for i in range(len(saved_categories))]:
                chosen_category = saved_categories[int(user_input)]
                remove_category(chosen_category)
                print(
                    chosen_category.title()
                    + " deleted from the list of saved categories."
                )
                break
            else:
                print(
                    f"Invalid input. Select a category by entering the corresponding number 0-{len(saved_categories)-1}."
                )
                continue


def prompt_add_monthly_transaction() -> None:
    """
    Prompt user to add a new monthly transaction to the list of saved monthly transactions.

    :return: None
    :rtype: None
    """
    while True:
        transaction_type = prompt_type()
        transaction_amount = prompt_amount()
        transaction_category = prompt_category()
        transaction_description = input("Description: ").strip()

        new_transaction = {
            "Type": transaction_type,
            "Amount": transaction_amount,
            "Category": transaction_category,
            "Description": transaction_description,
        }
        try:
            save_monthly_transaction(new_transaction)
            print("Transaction added to the list of saved monthly transactions.")
            break
        except ValueError:
            print("Transaction already in the list of saved monthly transactions.")
            break


def prompt_delete_monthly_transaction() -> None:
    """
    Prompt user to delete a monthly transaction from the list of saved monthly transactions.

    :return: None
    :rtype: None
    """
    if len(get_saved_monthly_transactions()) == 0:
        print("The list of saved monthly transactions is empty.")
    else:
        display_monthly_transactions()
        while True:
            user_input = input("Select a monthly transaction: ").strip()
            try:
                index = int(user_input)
                target_monthly_transaction = get_saved_monthly_transactions()[index]
                remove_monthly_transaction(target_monthly_transaction)
                print(
                    "Transaction deleted from the list of saved monthly transactions."
                )
                break
            except (ValueError, IndexError):
                print(
                    f"Invalid input. Select a transaction 0-{len(get_saved_monthly_transactions())-1}."
                )
                continue


def prompt_target_monthly_savings() -> None:
    """
    Prompt user to specify a new target monthly savings.

    :return: None
    :rtype: None
    """
    while True:
        user_target_monthly_savings_input = input(
            "Target monthly savings [non-negative float]: "
        ).strip()
        try:
            new_target_monthly_savings = float(user_target_monthly_savings_input)
            set_target_monthly_savings(new_target_monthly_savings)
            print(
                "Target monthly savings set to "
                + custom_format_amount(get_target_monthly_savings())
            )
            break
        except ValueError:
            print("Invalid input. Please enter a non-negative float.")
            continue


# ==========================================
# DISPLAY FUNCTIONS
# ==========================================


def display_main_menu() -> None:
    """
    Prints the main menu.

    :return: None
    :rtype: None
    """
    main_options = [
        ["View the current month's overview"],
        ["Add a one-time expense"],
        ["Add a transaction"],
        ["Modify a transaction"],
        ["Delete a transaction"],
        ["Add saved monthly transactions to the current month"],
        ["View a specific month's summary"],
        ["Search transactions"],
        ["Settings"],
        ["Help"],
        ["Exit"],
    ]
    print()
    print(
        tabulate(
            main_options,
            headers=["Main Menu"],
            tablefmt="fancy_grid",
            showindex="always",
        )
    )
    print()


def display_saved_categories() -> None:
    """
    Prints the list of saved categories.

    :return: None
    :rtype: None
    """
    saved_categories = [[category.title()] for category in get_saved_categories()]
    print()
    print(
        tabulate(
            saved_categories,
            headers=["Saved Categories"],
            tablefmt="fancy_grid",
            showindex="always",
        )
    )
    print()


def display_settings_menu() -> None:
    """
    Prints the settings menu.

    :return: None
    :rtype: None
    """
    settings_options = [
        ["View settings"],
        ["Modify locale"],
        ["Modify currency"],
        ["Add a category to the list of saved categories"],
        ["Delete a category from the list of saved categories"],
        ["Add a monthly transaction to the list of saved monthly transactions"],
        ["Delete a monthly transaction from the list of saved monthly transactions"],
        ["Modify target monthly savings"],
        ["Go back to the main Menu"],
    ]
    print()
    print(
        tabulate(
            settings_options,
            headers=["Settings Menu"],
            tablefmt="fancy_grid",
            showindex="always",
        )
    )
    print()


def display_current_month_overview() -> None:
    """
    Display current month's overview.

    :return: None
    :rtype: None
    """
    current_month_overview = generate_current_month_overview()
    print()
    print("Current month's overview:")
    print(tabulate(current_month_overview, tablefmt="rounded_grid"))
    print()
    print()
    input("[Press Enter to go back to the Main Menu] ")


def display_month_summary(target_month: str) -> None:
    """
    Display summary of the target month and top 10 categories in terms of total expense.

    :param target_month: Target month in YYYY-MM format.
    :type target_month: str
    :raise ValueError: If target_month is not a valid month or is not given in the expected format.
    :return: None
    :rtype: None
    """
    target_month_overview = generate_month_overview(target_month)
    first_of_target_month = date.fromisoformat(target_month + "-01")
    print()
    print(
        f"Summary of {format_date(first_of_target_month, format='MMMM yyyy', locale='en_US')}:"
    )
    print(tabulate(target_month_overview, tablefmt="rounded_grid"))
    top_expenses_by_category = generate_monthly_top_expenses_by_category(
        target_month, 10
    )
    print()
    print(
        f"Top 10 expense categories in {format_date(first_of_target_month, format='MMMM yyyy', locale='en_US')}:"
    )
    print(tabulate(top_expenses_by_category, headers="keys", tablefmt="rounded_grid"))
    print()
    print()
    input("[Press Enter to go back to the Main Menu] ")


def display_settings() -> None:
    """
    Display the current settings.

    :return: None
    :rtype: None
    """
    settings_overview = generate_settings_overview()
    print()
    print(tabulate(settings_overview, headers="keys", tablefmt="rounded_grid"))
    print()
    print()
    input("[Press Enter to go back to the Main Menu] ")


def display_monthly_transactions() -> None:
    """
    Display the list of saved monthly transactions.

    :return: None
    :rtype: None
    """
    monthly_transactions = generate_saved_monthly_transactions_list()
    print()
    print(
        tabulate(
            monthly_transactions,
            headers="keys",
            tablefmt="fancy_grid",
            showindex="always",
        )
    )
    print()


def display_transactions(transaction_list: list[dict]) -> None:
    """
    Display the list of transactions.

    :param transaction_list: The list of transactions to be displayed.
    :type transaction_list: list
    :return: None
    :rtype: None
    """
    formatted_transactions = generate_transaction_list(
        transaction_list,
        ["Date", "Type", "Amount", "Category", "Frequency", "Description"],
    )
    print()
    print(
        tabulate(
            formatted_transactions,
            headers="keys",
            tablefmt="fancy_grid",
            showindex="always",
        )
    )
    print()


def display_greeting() -> None:
    """
    Greet the user when they first open the app.

    :return: None
    :rtype: None
    """
    print()
    print("Welcome to the Expense Tracker!")


def display_help() -> None:
    """
    Display some help on how to use the app.

    :return: None
    :rtype: None
    """
    print()
    print("[Purpose]")
    print()
    print("Expense/income tracker with some budgeting functionality.")
    print()
    print()
    print("[Storage]")
    print()
    print(
        "All data is stored only locally. The settings are stored in settings.json, and the transactions are stored in transactions.csv."
    )
    print()
    print("The setting keys are:")
    print("* 'locale' ('en_US' by default).")
    print("* 'currency' ('USD' by default).")
    print("* 'saved_categories' (empty list by default).")
    print("* 'saved_monthly_transactions' (empty list by default).")
    print("* 'target_monthly_savings' (0.0 by default).")
    print("* 'last_modified'.")
    print()
    print("The transaction headers are:")
    print("* 'ID' (uniquely assigned to each transaction upon writing).")
    print("* 'Date' (stored in YYYY-MM-DD format).")
    print("* 'Type' (either expense or income).")
    print("* 'Amount' (a non-negative float).")
    print("* 'Category'.")
    print("* 'Frequency' (either one-time or monthly).")
    print("* 'Description'.")
    print()
    print()
    print("[Functionality]")
    print()
    print("* Use the menus to choose the desired option.")
    print("* Saved categories can be used to label transactions more rapidly.")
    print(
        "* Saved monthly transactions can be added to the current month automatically."
    )
    print("* Regular expressions can be used to search for transactions.")
    print(
        "* Regular expressions can also be used when specifying the date of a transaction to be modified or deleted."
    )
    print(
        "* The current month's overview will display the current target daily budget."
    )
    print(
        "* The current target daily budget does not take the current day's one-time expenses into account."
    )
    print("* The calculation of the current target daily budget is based on")
    print("    * the current month's total income,")
    print("    * the current month's total fixed (=monthly) expense,")
    print("    * the target monthly savings,")
    print("    * and the current month's daily average variable (=one-time) expense.")
    print(
        "* Month summaries contain a list of top 10 categories with largest total expense during that month."
    )
    print()
    print()
    input("[Press Enter to go back to the Main Menu] ")


def display_farewell() -> None:
    """
    Bid farewell to the user when they close the app.

    :return: None
    :rtype: None
    """
    print()
    print("Bye!")
    print()


if __name__ == "__main__":
    main()
