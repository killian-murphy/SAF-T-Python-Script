# Import dependencies
import pandas as pd
import bs4

from datetime import datetime as dt


def reconcile_tables(dataset_transactions: type(pd.DataFrame()), dataset_accounts: type(pd.DataFrame())) -> pd.DataFrame():
    """
        Join the Dataset Transactions and Dataset Accounts by Account ID
        - Calculate Difference between Transaction Amount and Movement between Opening and Closing Balances
        
        Inputs
        --------------------
            dataset_transactions ( Pandas Dataframe ): Table of Accounts, and Transaction amounts
            dataset_accounts     ( Pandas Dataframe ): Table of Accounts, Opening, and Closing amounts
        
        Outputs
        --------------------
            account_movement ( Pandas Dataframe ): Table of Accounts, Opening, Closing, and Transaction amounts
    """
    # Reconciliation
    net_transactions = dataset_transactions[['Account ID','Transaction Amount, +/-']].groupby(by=['Account ID']).sum()
    dataset_accounts['Net Movement, Balance'] = dataset_accounts['Closing Balance Amount, +/-'] - dataset_accounts['Opening Balance Amount, +/-']
    account_movement = dataset_accounts.join(net_transactions, how='outer', on= 'Account ID')
    account_movement['Difference'] = account_movement['Net Movement, Balance'].fillna(value=0) - account_movement['Transaction Amount, +/-'].fillna(value=0)
    
    return account_movement

def print_controlchecks_transactions(dataset_transactions: type(pd.DataFrame()), file_xml: type(bs4.BeautifulSoup(features="lxml"))):
    """
        Print Transaction Count and Amounts, reconciled to Control Tags within the SAF-T file
        
        Inputs
        --------------------
            dataset_transactions ( Pandas Dataframe ): Table of Accounts, and Transaction amounts
            account_movement: Pandas Dataframe, Table of Accounts, Opening, Closing, and Transaction amounts
        
        Outputs
        --------------------
            print Transaction Count Flag, Transaction Count Calculated, and Difference between the value value and the calculated / extracted value
            print Transaction Amount Flag, Transaction Amount Calculated, and Difference between the value value and the calculated / extracted value 
    """
    
    # Print Control Checks to Console
    # Transaction Count
    transactions_count_flag = int(file_xml.find('n1:generalledgerentries').find('n1:numberofentries').get_text(strip=True))
    transactions_count_calc = len(file_xml.find('n1:generalledgerentries').find('n1:journal').find_all('n1:transaction'))
    print('----------------------------------')
    print('Transaction Count\nControl:    {0:4}\nCalculated: {1:4}\nDifference: {2:4}'.format(transactions_count_flag, 
                                                                                            transactions_count_calc, 
                                                                                            transactions_count_flag-transactions_count_calc))
    
    
    total_debit_flag  = float(file_xml.find('n1:generalledgerentries').find('n1:totaldebit').get_text(strip=True))
    total_credit_flag = float(file_xml.find('n1:generalledgerentries').find('n1:totalcredit').get_text(strip=True))
    
    total_debit_calc  = dataset_transactions[dataset_transactions['Transaction Flag']=='Debit' ]['Transaction Amount'].sum()
    total_credit_calc = dataset_transactions[dataset_transactions['Transaction Flag']=='Credit']['Transaction Amount'].sum()
    
    total_debit_diff  = total_debit_flag  - total_debit_calc
    total_credit_diff = total_credit_flag - total_credit_calc
    
    print('----------------------------------')
    print('Transaction Amount\n             Debit        Credit \nControl:    {0:12.2f} {1:12.2f} \nCalculated: {2:12.2f} {3:12.2f}\nDifference: {4:12.2f} {5:12.2f}'.format(
                                        total_debit_flag, total_credit_flag,
                                        total_debit_calc, total_credit_calc,
                                        total_debit_diff, total_credit_diff))
    
def print_reconciliation_accountmovement_transactions(account_movement: type(pd.DataFrame())):
    """
        Print each account which has a non-zero difference between the Account Movement and the Transaction Amount:
             Opening Balance
           - Closing Balance
           ____________________
             Account Movement
           - Transaction Amount
           ____________________
             Difference
        
        Print the Absolute and Net Difference for all accounts
        
        Inputs
        --------------------
            account_movement ( Pandas Dataframe ): Table of Accounts, Opening, Closing, and Transaction amounts
        
        Outputs
        --------------------
            print Differences by Accounts
            print Differences for all Accounts
    """
    # Print Reconciliation to Console
    print('----------------------------------')
    print('Accounts with non-Zero Difference: \nCount: {0:3}'.format(account_movement[account_movement['Difference'] != 0]['Difference'].count()))
    print('----------------------------------')
    
    for account in account_movement[account_movement['Difference'] != 0]['Account ID']:
        print('Account ID: {0}'.format(account))
        print('Absolute Difference: {0:10.2f}'.format(account_movement[account_movement['Account ID'] == account]['Difference'].abs().sum()))
        print('Net Difference:      {0:10.2f}'.format(account_movement[account_movement['Account ID'] == account]['Difference'].sum()))
        print('----------------------------------')
    
    print('Total:')
    print('Absolute Difference: {0:10.2f}'.format(account_movement['Difference'].abs().sum()))
    print('Net Difference:      {0:10.2f}'.format(account_movement['Difference'].sum()))
    print('----------------------------------')
    
def export_table(folder_path: str, file_name: str, table: type(pd.DataFrame())):
    """
        Export Table to CSV
        
        Inputs
        --------------------
            folder_path ( string ):           Folder Path
            file_name   ( string ):           Table Name
            table       ( Pandas Dataframe ): Table of Accounts, Opening, Closing, and Transaction amounts
        
        Outputs
        --------------------
            CSV File with name formatted: '[ Table Name ] Table - Extract YYYY-MM-DD HHMMSS.csv'
    """
    table.to_csv(folder_path.format( file_name ,  dt.now().strftime("%Y-%m-%d %H%M%S")))
    
    