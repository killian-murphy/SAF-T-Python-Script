"""
	Import SAF-T file and extract accounts as flat table to CSV file.
"""
# Import dependencies
from bs4                import BeautifulSoup        as bs
from L00_SAFT_setup     import setup_options
from L02_SAFT_functions import extract_accounts
from L02_SAFT_functions import extract_transactions
from L03_SAFT_reporting import print_controlchecks_transactions
from L03_SAFT_reporting import print_reconciliation_accountmovement_transactions
from L03_SAFT_reporting import export_table
from L03_SAFT_reporting import reconcile_tables

# Set up options
setup_options()

# Set Import Path
file_path_import = r'C:\Users\KM_Personal\Desktop\SAF-T Example File.txt'

# Set Export Path
file_path_export = r'C:\Users\KM_Personal\Desktop\{0} - Extract {1}.csv'

# Read TXT file and convert to XML
file_txt = open(file_path,'r')
file_xml = bs(file_txt, 'lxml')

# Extract Transactions and Account tables from SAF-T file
dataset_transactions = extract_transactions(file_xml)
dataset_accounts     = extract_accounts(file_xml)

# Reconcile Accounts and Transactions
account_movement = reconcile_tables(dataset_transactions, dataset_accounts)

# Print Control Checks
print_controlchecks_transactions(dataset_transactions, file_xml)
print_reconciliation_accountmovement_transactions(account_movement)

# Export Tables
export_table(file_path_export, 'Accounts Table',         dataset_accounts    )
export_table(file_path_export, 'Transactions Table',     dataset_transactions)
export_table(file_path_export, 'Account Movement Table', account_movement    )
