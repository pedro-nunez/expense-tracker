# EXPENSE TRACKER

Expense Tracker is a command-line application for tracking income, expenses, saved categories, recurring monthly transactions, and monthly budgeting targets.

This project began as my final project for CS50's Introduction to Programming with Python. The original CS50 demo video is available here: <https://youtu.be/Sug23j4czA8>.

### How to use the Expense Tracker

* Use the menus to choose the desired option.
* Saved categories can be used to label transactions more rapidly.
* Saved monthly transactions can be added to the current month automatically.
* Regular expressions can be used to search for transactions.
* Regular expressions can also be used when specifying the date of a transaction to be modified or deleted.
* The current month's overview will display the current target daily budget.
* The current target daily budget does not take the current day's one-time expenses into account.
* The calculation of the current target daily budget is based on
    * the current month's total income,
    * the current month's total fixed (=monthly) expense,
    * the target monthly savings,
    * and the current month's daily average variable (=one-time) expense.
* Month summaries contain a list of top 10 categories with largest total expense during that month.

### Architecture

The project is structured into three layers:

* Data layer: Read and write files from storage, performing only structural and type checks.
* Logic layer: Operate on transactions and lists of transactions and perform logic and semantic checks when the read and write functions from the data layer are called.
* UI layer: Prompt and take input from the user, validate the input and display requested information.

Ideally, each layer would be in a separate module: data.py, logic.py, and ui.py. However, in order to comply with the final project's requirements from the course, the layers are currently kept in a single module.

The testing module test\_project.py imports examples.py to generate example settings and transactions, and it does not alter the actual settings and transactions files of the project.

### Storage

All data is stored only locally. The settings are stored in settings.json, and the transactions are stored in transactions.csv.

The setting keys are:

* 'locale' ('en\_US' by default).
* 'currency' ('USD' by default).
* 'saved\_categories' (empty list by default).
* 'saved\_monthly\_transactions' (empty list by default).
* 'target\_monthly\_savings' (0.0 by default).
* 'last\_modified'.

The transaction headers are:

* 'ID' (uniquely assigned to each transaction upon writing).
* 'Date' (stored in YYYY-MM-DD format).
* 'Type' (either expense or income).
* 'Amount' (a non-negative float).
* 'Category'.
* 'Frequency' (either one-time or monthly).
* 'Description'.

### Some design choices

* Single module and test module to comply with the final project's requirements from the course.
* Storing the transactions on a csv file makes the project more portable and flexible. It also makes it easier to create backups, exports, import data, analyze data and plot data, if desired.
* The Average Daily Expense and the Target Daily Budget do not take the current day into account. The logic behind this decision is that adding the transactions of half the current day into the computation would give a misleading Average Daily Expense, especially during the first days of the month.
* Saved categories are only used for quick labeling. A transaction's category does not have to belong to the list of saved categories. The logic behind this decision is that the user's saved categories may change over time.
* Saved monthly transactions are stored without Date and are added to the first day of the month by default. The user can still add monthly transactions manually on later days of the month, or change the Date of a monthly transaction that was saved on the first of the month.
* Saved monthly transactions have to be unique. If the user wants to have the same monthly transaction saved more than once, so that it is saved more than once each month, then they can distinguish them using the Description field.

### Potential room for future improvement

* Separate the three layers into different modules, and write several smaller test modules instead of a single large tests module.
* Include some data analysis and plotting functionality within the app.
* Include data export/import functionality within the app.
* Allow for monthly category-wise budgeting, not just global budgeting.
* Allow other frequencies, such as quarterly or yearly.
