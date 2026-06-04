import pytest
from project import *
import examples
import json
import csv
from datetime import date

# ==========================================
# DATA TESTS
# ==========================================


"""
Our data layer reads and writes from the current working directory. We use tmp_path to create a temporary directory and monkeypatch to change the working directory to this temporary path.
"""


def test_init_settings(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings_file = tmp_path / "settings.json"

    init_settings()

    assert settings_file.exists()

    with open(settings_file, "r") as file:
        content = json.load(file)

    expected_keys = examples.generate_settings_keys()

    assert set(content.keys()) == expected_keys
    assert content["locale"] == "en_US"
    assert content["currency"] == "USD"
    with pytest.raises(FileExistsError):
        init_settings()


def test_load_settings(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError):
        load_settings()

    settings_with_missing_value = examples.generate_example_settings()
    del settings_with_missing_value["currency"]

    with open("settings.json", "w") as file:
        json.dump(settings_with_missing_value, file)
    with pytest.raises(KeyError):
        load_settings()

    settings_with_extra_value = examples.generate_example_settings()
    settings_with_extra_value["animal"] = "cat"
    with open("settings.json", "w") as file:
        json.dump(settings_with_extra_value, file)
    with pytest.raises(KeyError):
        load_settings()

    settings_with_invalid_locale = examples.generate_example_settings()
    settings_with_invalid_locale["locale"] = 0.0
    with open("settings.json", "w") as file:
        json.dump(settings_with_invalid_locale, file)
    with pytest.raises(TypeError):
        load_settings()

    invalid_settings = [
        "en_US",
        "USD",
        [],
        [],
        0.0,
        "2000-01-01",
    ]
    with open("settings.json", "w") as file:
        json.dump(invalid_settings, file)
    with pytest.raises(ValueError):
        load_settings()


def test_update_settings(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    init_settings()

    valid_settings = examples.generate_example_settings()

    update_settings(valid_settings)
    with open("settings.json", "r") as file:
        content = json.load(file)
    assert content["currency"] == "EUR"
    assert content["target_monthly_savings"] == 200.0
    assert content["saved_categories"] == [
        "eating out",
        "gifts",
        "groceries",
        "rent",
        "salary",
        "shopping",
        "transportation",
    ]
    assert content["last_modified"] == date.today().isoformat()

    invalid_settings = valid_settings.copy()
    invalid_settings["locale"] = 0.0
    with pytest.raises(TypeError):
        update_settings(invalid_settings)

    invalid_settings["locale"] = "en_US"
    invalid_settings["animal"] = "cat"
    with pytest.raises(KeyError):
        update_settings(invalid_settings)

    del invalid_settings["animal"]
    del invalid_settings["currency"]
    del invalid_settings["saved_monthly_transactions"]
    with pytest.raises(KeyError):
        update_settings(invalid_settings)


def test_init_transactions(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transactions_file = tmp_path / "transactions.csv"

    init_transactions()

    assert transactions_file.exists()

    with open(transactions_file, "r") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames

    assert headers == examples.generate_transaction_headers()
    with pytest.raises(FileExistsError):
        init_transactions()


def test_load_transactions(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transactions_file = tmp_path / "transactions.csv"

    with pytest.raises(FileNotFoundError):
        load_transactions()

    headers = examples.generate_transaction_headers()
    transactions = examples.generate_example_transactions()

    for i in range(len(headers)):
        invalid_headers = headers.copy()
        del invalid_headers[i]
        with open(transactions_file, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=invalid_headers)
            writer.writeheader()
        with pytest.raises(ValueError):
            load_transactions()

    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

    transaction_with_invalid_amount = transactions[0].copy()
    transaction_with_invalid_amount["Amount"] = "cat"
    with open(transactions_file, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerow(transaction_with_invalid_amount)
    with pytest.raises(ValueError):
        load_transactions()

    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

    transaction = transactions[0].copy()
    with open(transactions_file, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerow(transaction)

    loaded_transactions = load_transactions()
    assert loaded_transactions[0]["Type"] == "income"
    assert loaded_transactions[0]["Amount"] == 500.0


def test_save_transaction(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transactions_file = tmp_path / "transactions.csv"

    headers = examples.generate_transaction_headers()
    transactions = examples.generate_example_transactions()

    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

    # Input transactions should not have an ID, so we delete it.
    del transactions[0]["ID"]
    example_transaction = transactions[0].copy()
    save_transaction(example_transaction)

    saved_transactions = []
    with open(transactions_file, "r", newline="") as file:
        reader = csv.DictReader(file)
        for transaction in reader:
            saved_transactions.append(transaction)

    assert saved_transactions[0]["Type"] == "income"
    assert saved_transactions[0]["Category"] == "salary"
    assert "ID" in saved_transactions[0]

    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

    transaction_with_missing_value = transactions[0].copy()
    del transaction_with_missing_value["Frequency"]
    with pytest.raises(KeyError):
        save_transaction(transaction_with_missing_value)

    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

    transaction_with_extra_value = transactions[0].copy()
    transaction_with_extra_value["Animal"] = "cat"
    with pytest.raises(KeyError):
        save_transaction(transaction_with_extra_value)

    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

    transaction_with_non_string_category = transactions[0].copy()
    transaction_with_non_string_category["Category"] = 5
    with pytest.raises(TypeError):
        save_transaction(transaction_with_non_string_category)

    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

    transaction_with_non_float_amount = transactions[0].copy()
    transaction_with_non_float_amount["Amount"] = 5
    with pytest.raises(TypeError):
        save_transaction(transaction_with_non_float_amount)


def test_delete_transaction(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transactions_file = tmp_path / "transactions.csv"

    headers = examples.generate_transaction_headers()
    transactions = examples.generate_example_transactions()

    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

    example_transactions = [
        transactions[0].copy(),
        transactions[1].copy(),
        transactions[14].copy(),
        transactions[2].copy(),
        transactions[3].copy(),
    ]

    with open(transactions_file, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        for transaction in example_transactions:
            writer.writerow(transaction)

    saved_transactions = []
    with open(transactions_file, "r", newline="") as file:
        reader = csv.DictReader(file)
        for transaction in reader:
            saved_transactions.append(transaction)

    assert saved_transactions[0]["ID"] == "1"
    assert saved_transactions[1]["ID"] == "2"
    assert saved_transactions[2]["ID"] == "287"
    assert saved_transactions[3]["ID"] == "3"
    assert saved_transactions[4]["ID"] == "4"

    delete_transaction("2")

    saved_transactions = []
    with open(transactions_file, "r", newline="") as file:
        reader = csv.DictReader(file)
        for transaction in reader:
            saved_transactions.append(transaction)

    assert saved_transactions[0]["ID"] == "1"
    assert saved_transactions[1]["ID"] == "287"
    assert saved_transactions[2]["ID"] == "3"
    assert saved_transactions[3]["ID"] == "4"

    delete_transaction("4")

    saved_transactions = []
    with open(transactions_file, "r", newline="") as file:
        reader = csv.DictReader(file)
        for transaction in reader:
            saved_transactions.append(transaction)

    assert saved_transactions[0]["ID"] == "1"
    assert saved_transactions[1]["ID"] == "287"
    assert saved_transactions[2]["ID"] == "3"

    delete_transaction("287")

    saved_transactions = []
    with open(transactions_file, "r", newline="") as file:
        reader = csv.DictReader(file)
        for transaction in reader:
            saved_transactions.append(transaction)

    assert saved_transactions[0]["ID"] == "1"
    assert saved_transactions[1]["ID"] == "3"

    with pytest.raises(KeyError):
        delete_transaction("10000")

    with pytest.raises(KeyError):
        delete_transaction("cat")

    with open(transactions_file, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerow(example_transactions[3])

    with pytest.raises(KeyError):
        delete_transaction("3")


def test_update_transaction(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transactions_file = tmp_path / "transactions.csv"

    headers = examples.generate_transaction_headers()
    transactions = examples.generate_example_transactions()

    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

    example_transactions = [
        transactions[0].copy(),
        transactions[1].copy(),
        transactions[14].copy(),
        transactions[2].copy(),
        transactions[3].copy(),
    ]

    with open(transactions_file, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        for transaction in example_transactions:
            writer.writerow(transaction)

    saved_transactions = []
    with open(transactions_file, "r", newline="") as file:
        reader = csv.DictReader(file)
        for transaction in reader:
            saved_transactions.append(transaction)

    assert saved_transactions[0]["ID"] == "1"
    assert saved_transactions[1]["ID"] == "2"
    assert saved_transactions[2]["ID"] == "287"
    assert saved_transactions[3]["ID"] == "3"
    assert saved_transactions[4]["ID"] == "4"

    update_transaction("3", "Description", "Breakfast")
    update_transaction("4", "Description", "Bus ticket")
    update_transaction("4", "Frequency", "one-time")
    update_transaction("1", "Amount", 600.0)
    update_transaction("287", "Category", "shopping")
    update_transaction("4", "Description", "Bus")
    update_transaction("287", "Description", "")

    saved_transactions = []
    with open(transactions_file, "r", newline="") as file:
        reader = csv.DictReader(file)
        for transaction in reader:
            saved_transactions.append(transaction)

    assert saved_transactions[0]["ID"] == "1"
    assert saved_transactions[1]["ID"] == "2"
    assert saved_transactions[2]["ID"] == "287"
    assert saved_transactions[3]["ID"] == "3"
    assert saved_transactions[4]["ID"] == "4"

    assert saved_transactions[3]["Type"] == "expense"
    assert saved_transactions[3]["Amount"] == "1.0"
    assert saved_transactions[3]["Description"] == "Breakfast"
    assert saved_transactions[1]["Amount"] == "100.0"
    assert saved_transactions[1]["Frequency"] == "monthly"
    assert saved_transactions[4]["Description"] == "Bus"
    assert saved_transactions[4]["Frequency"] == "one-time"
    assert saved_transactions[0]["Amount"] == "600.0"
    assert saved_transactions[2]["Category"] == "shopping"
    assert saved_transactions[2]["Description"] == ""

    with pytest.raises(KeyError):
        update_transaction("10000", "Type", "income")

    with pytest.raises(KeyError):
        update_transaction("cat", "Type", "expense")

    with pytest.raises(TypeError):
        update_transaction("2", "Type", 3)

    with pytest.raises(TypeError):
        update_transaction("2", "Amount", "50.0")


# ==========================================
# LOGIC TESTS
# ==========================================


def test_filter_transactions():
    with pytest.raises(TypeError):
        filter_transactions(5, ".*", ".*", ".*", 0.0, ".*", ".*", ".*")

    with pytest.raises(TypeError):
        filter_transactions(["cat"], ".*", ".*", ".*", 0.0, ".*", ".*", ".*")

    example_transactions = examples.generate_example_transactions()

    transactions_filtered_by_id = filter_transactions(
        example_transactions, "^3$", ".*", ".*", 0.0, ".*", ".*", ".*"
    )
    assert [transaction["ID"] for transaction in transactions_filtered_by_id] == ["3"]

    transactions_filtered_by_id = filter_transactions(
        example_transactions, "^1.*$", ".*", ".*", 0.0, ".*", ".*", ".*"
    )
    assert [transaction["ID"] for transaction in transactions_filtered_by_id] == [
        "1",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
    ]

    transactions_filtered_by_year = filter_transactions(
        example_transactions, ".*", "^1999-..-..$", ".*", 0.0, ".*", ".*", ".*"
    )
    assert [transaction["ID"] for transaction in transactions_filtered_by_year] == [
        "14",
        "15",
        "16",
        "17",
        "18",
    ]

    transactions_filtered_by_month = filter_transactions(
        example_transactions, ".*", "^2000-02-..$", ".*", 0.0, ".*", ".*", ".*"
    )
    assert [transaction["ID"] for transaction in transactions_filtered_by_month] == [
        "19",
        "20",
    ]

    transactions_filtered_by_date = filter_transactions(
        example_transactions, ".*", "^2000-01-21$", ".*", 0.0, ".*", ".*", ".*"
    )
    assert [transaction["ID"] for transaction in transactions_filtered_by_date] == [
        "12"
    ]

    transactions_filtered_by_type = filter_transactions(
        example_transactions, ".*", ".*", "income", 0.0, ".*", ".*", ".*"
    )
    assert [transaction["ID"] for transaction in transactions_filtered_by_type] == [
        "1",
        "6",
        "17",
    ]

    transactions_filtered_by_amount = filter_transactions(
        example_transactions, ".*", ".*", ".*", 100.0, ".*", ".*", ".*"
    )
    assert [transaction["ID"] for transaction in transactions_filtered_by_amount] == [
        "1",
        "2",
        "17",
        "18",
    ]

    transactions_filtered_by_category = filter_transactions(
        example_transactions, ".*", ".*", ".*", 0.0, "(shopping|gifts)", ".*", ".*"
    )
    assert [transaction["ID"] for transaction in transactions_filtered_by_category] == [
        "6",
        "7",
        "9",
    ]

    transactions_filtered_by_frequency = filter_transactions(
        example_transactions, ".*", ".*", ".*", 0.0, ".*", "^month.*$", ".*"
    )
    assert [
        transaction["ID"] for transaction in transactions_filtered_by_frequency
    ] == ["1", "2", "4", "17", "18"]

    transactions_filtered_by_description = filter_transactions(
        example_transactions, ".*", ".*", ".*", 0.0, ".*", ".*", "^$"
    )
    assert [
        transaction["ID"] for transaction in transactions_filtered_by_description
    ] == ["9", "287"]

    transactions_filtered_by_description = filter_transactions(
        example_transactions,
        ".*",
        ".*",
        ".*",
        0.0,
        ".*",
        ".*",
        "\\b[Gg][Ii][Ff][Tt]\\b",
    )
    assert [
        transaction["ID"] for transaction in transactions_filtered_by_description
    ] == ["6", "7"]

    transactions_filtered_by_date_and_amount_and_category = filter_transactions(
        example_transactions, ".*", "2000-01-16", ".*", 1.5, "eating out", ".*", ".*"
    )
    assert [
        transaction["ID"]
        for transaction in transactions_filtered_by_date_and_amount_and_category
    ] == ["10"]


def test_filter_transactions_between_dates():
    with pytest.raises(TypeError):
        filter_transactions_between_dates(5, "1999-01-01", "2000-01-01")

    with pytest.raises(TypeError):
        filter_transactions_between_dates(["cat"], "1999-01-01", "2000-01-01")

    example_transactions = examples.generate_example_transactions()

    with pytest.raises(TypeError):
        filter_transactions_between_dates(example_transactions, 5, "2000-01-01")

    with pytest.raises(TypeError):
        filter_transactions_between_dates(example_transactions, "1999-01-01", 2000)

    with pytest.raises(ValueError):
        filter_transactions_between_dates(
            example_transactions, "1999-13-01", "2000-01-01"
        )

    with pytest.raises(ValueError):
        filter_transactions_between_dates(
            example_transactions, "1999-01-01", "2000-01-32"
        )

    filtered_transactions_1 = filter_transactions_between_dates(
        example_transactions, "1999-12-02", "2000-01-01"
    )
    assert [transaction["ID"] for transaction in filtered_transactions_1] == [
        "1",
        "2",
        "3",
        "4",
        "14",
        "15",
        "16",
    ]

    filtered_transactions_2 = filter_transactions_between_dates(
        example_transactions, "0001-01-01", "1998-01-01"
    )
    assert [transaction["ID"] for transaction in filtered_transactions_2] == ["287"]

    filtered_transactions_3 = filter_transactions_between_dates(
        example_transactions, "2000-01-01", "1999-01-01"
    )
    assert [transaction["ID"] for transaction in filtered_transactions_3] == []


def test_sort_transactions():
    with pytest.raises(TypeError):
        sort_transactions(5, [])

    with pytest.raises(TypeError):
        sort_transactions(["cat"], [])

    example_transactions = examples.generate_example_transactions()

    with pytest.raises(TypeError):
        sort_transactions(example_transactions, 0.0)

    with pytest.raises(KeyError):
        sort_transactions(example_transactions, ["Date", "Animal"])

    with pytest.raises(ValueError):
        sort_transactions(example_transactions, ["Amount", "Category", "Amount"])

    sorted_transactions_1 = sort_transactions(example_transactions, ["Description"])
    assert [transaction["ID"] for transaction in sorted_transactions_1] == [
        "287",
        "9",
        "7",
        "20",
        "6",
        "3",
        "8",
        "11",
        "19",
        "12",
        "14",
        "16",
        "5",
        "13",
        "15",
        "10",
        "4",
        "18",
        "2",
        "17",
        "1",
    ]

    sorted_transactions_2 = sort_transactions(
        example_transactions, ["Amount", "Category"]
    )
    assert [transaction["ID"] for transaction in sorted_transactions_2] == [
        "17",
        "1",
        "18",
        "2",
        "287",
        "4",
        "5",
        "9",
        "13",
        "7",
        "16",
        "10",
        "12",
        "6",
        "14",
        "15",
        "20",
        "3",
        "8",
        "11",
        "19",
    ]

    sorted_transactions_3 = sort_transactions(
        example_transactions, ["Category", "Amount"]
    )
    assert [transaction["ID"] for transaction in sorted_transactions_3] == [
        "10",
        "12",
        "15",
        "20",
        "3",
        "8",
        "11",
        "19",
        "7",
        "6",
        "5",
        "13",
        "16",
        "14",
        "18",
        "2",
        "17",
        "1",
        "9",
        "287",
        "4",
    ]

    sorted_transactions_4 = sort_transactions(example_transactions, [])
    assert [transaction["ID"] for transaction in sorted_transactions_4] == [
        "287",
        "17",
        "18",
        "14",
        "15",
        "16",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "19",
        "20",
    ]


def test_add_monthly_transactions(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings_file = tmp_path / "settings.json"
    transactions_file = tmp_path / "transactions.csv"

    with pytest.raises(FileNotFoundError):
        add_monthly_transactions("2000-03")

    example_settings = examples.generate_example_settings()
    with open(settings_file, "w") as file:
        json.dump(example_settings, file)

    example_transactions = examples.generate_example_transactions()
    headers = examples.generate_transaction_headers()
    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for transaction in example_transactions:
            writer.writerow(transaction)

    with pytest.raises(ValueError):
        add_monthly_transactions("2000-13")

    with pytest.raises(ValueError):
        add_monthly_transactions("2000-01")

    add_monthly_transactions("2000-02")
    saved_transactions = []
    with open(transactions_file, "r", newline="") as file:
        reader = csv.DictReader(file)
        for transaction in reader:
            saved_transactions.append(transaction)

    assert {
        key: value for key, value in saved_transactions[21].items() if key != "ID"
    } == {
        "Date": "2000-02-01",
        "Type": "income",
        "Amount": "500.0",
        "Category": "salary",
        "Frequency": "monthly",
        "Description": "Salary",
    }
    assert {
        key: value for key, value in saved_transactions[22].items() if key != "ID"
    } == {
        "Date": "2000-02-01",
        "Type": "expense",
        "Amount": "100.0",
        "Category": "rent",
        "Frequency": "monthly",
        "Description": "Rent",
    }
    assert {
        key: value for key, value in saved_transactions[23].items() if key != "ID"
    } == {
        "Date": "2000-02-01",
        "Type": "expense",
        "Amount": "10.0",
        "Category": "transportation",
        "Frequency": "monthly",
        "Description": "Monthly Pass",
    }


def test_format_transaction(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings_file = tmp_path / "settings.json"

    example_transaction = examples.generate_example_transactions()[2]

    with pytest.raises(FileNotFoundError):
        format_transaction(example_transaction, ["Date"])

    example_settings = examples.generate_example_settings()
    with open(settings_file, "w") as file:
        json.dump(example_settings, file)

    with pytest.raises(KeyError):
        format_transaction(example_transaction, ["Date", "Animal"])

    with pytest.raises(ValueError):
        format_transaction(example_transaction, ["Date", "Date"])

    formatted_transaction = format_transaction(
        example_transaction,
        ["Frequency", "Amount", "Type", "Description", "Date", "Category"],
    )
    assert formatted_transaction == {
        "Frequency": "One-Time",
        "Amount": "1,00 €",
        "Type": "Expense",
        "Description": "Coffee",
        "Date": "1/1/00",
        "Category": "Eating Out",
    }

    example_transaction = examples.generate_example_transactions()[8]
    example_transaction["Amount"] = 7000.58
    formatted_transaction = format_transaction(
        example_transaction, ["Description", "Amount"]
    )
    assert formatted_transaction == {"Description": "", "Amount": "7.000,58 €"}


def test_calculate_total_amount():
    with pytest.raises(TypeError):
        calculate_total_amount(5)

    with pytest.raises(TypeError):
        calculate_total_amount(["cat"])

    invalid_transactions = examples.generate_example_transactions()
    del invalid_transactions[0]["Amount"]
    with pytest.raises(KeyError):
        calculate_total_amount(invalid_transactions)

    example_transactions = examples.generate_example_transactions()

    assert calculate_total_amount(example_transactions[:3]) == 601.0
    assert calculate_total_amount([]) == 0.0
    assert calculate_total_amount(example_transactions[7:8]) == 1.0


def test_calculate_average_daily_amount_between_dates():
    example_transactions = examples.generate_example_transactions()[:15]
    del example_transactions[0]
    del example_transactions[4]

    assert (
        calculate_average_daily_amount_between_dates(
            example_transactions, "2000-01-01", "2000-01-14"
        )
        == 8.785714285714286
    )
    assert (
        calculate_average_daily_amount_between_dates(
            example_transactions, "2000-01-06", "2000-01-06"
        )
        == 7.0
    )
    assert (
        calculate_average_daily_amount_between_dates(
            example_transactions, "2001-01-01", "2002-01-01"
        )
        == 0.0
    )

    with pytest.raises(ValueError):
        calculate_average_daily_amount_between_dates(
            example_transactions, "2000-01-06", "2000-01-05"
        )


def test_calculate_monthly_total(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transactions_file = tmp_path / "transactions.csv"

    example_transactions = examples.generate_example_transactions()
    headers = examples.generate_transaction_headers()
    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for transaction in example_transactions:
            writer.writerow(transaction)

    with pytest.raises(ValueError):
        calculate_monthly_total("2000-13", "expense", "rent", "monthly", "Rent")

    assert (
        calculate_monthly_total(
            "2000-01", "expense", "(eating out|groceries)", "one-time", ".*"
        )
        == 24.0
    )
    assert calculate_monthly_total("2000-01", "income", ".*", ".*", ".*") == 504.0
    assert calculate_monthly_total("2001-01", ".*", ".*", ".*", ".*") == 0.0


def test_calculate_monthly_expense_by_category(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    transactions_file = tmp_path / "transactions.csv"

    example_transactions = examples.generate_example_transactions()
    headers = examples.generate_transaction_headers()
    with open(transactions_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for transaction in example_transactions:
            writer.writerow(transaction)

    with pytest.raises(ValueError):
        calculate_monthly_expense_by_category("2000-13")

    assert calculate_monthly_expense_by_category("2000-01") == [
        {"Category": "rent", "Expense": 100.0},
        {"Category": "groceries", "Expense": 13.0},
        {"Category": "eating out", "Expense": 11.0},
        {"Category": "transportation", "Expense": 10.0},
        {"Category": "shopping", "Expense": 7.0},
        {"Category": "gifts", "Expense": 5.0},
    ]
    assert calculate_monthly_expense_by_category("2001-01") == []
    assert calculate_monthly_expense_by_category("1992-07") == [
        {"Category": "stationery", "Expense": 30.0},
    ]
