# Import dependencies
import bs4                    as bs
import pandas                 as pd

# Set Multiplier
multiplier = dict({ 'Debit' : -1,
                    'Credit':  1  })

def extract_transactions(xml_file: type(bs.BeautifulSoup(features="lxml"))) -> pd.DataFrame():
    """
        Extract Transactions Table from SAF-T XML file and export as Pandas DataFrame
        - Create calculated column from Credit/Debit field and Amount field 
        
        Inputs
        --------------------
            xml_file ( Beautiful Soup XML object ):    SAF-T file loaded as XML object
        
        Outputs
        --------------------
            dataset_transactions ( Pandas Dataframe ): Table of Transactions
    """
    # Initialise variables - Create temporary dictionary and list
    temp_list = list()
    temp_dict = dict()
    
    # For each Transaction in Transactions:
    #   For each Line in Transaction:
    #      Extract Fields:
    #          - Account ID
    #          - Transaction Amount
    #          - Transaction Flag
    
    for transaction in xml_file.find('n1:generalledgerentries').find('n1:journal').find_all('n1:transaction'):
        for general_ledger_line_entry in transaction.find_all('n1:line'):
            temp_dict = dict({'Account ID' : general_ledger_line_entry.find('n1:accountid').get_text(strip=True)})
            
            # Determine if the Transaction Amount is a Debit or a Credit
            # Add Transaction Amount and Transaction Flag (Debit/ Credit) to temp_dict
            if general_ledger_line_entry.find('n1:debitamount') is None:
                temp_dict['Transaction Amount'] = general_ledger_line_entry.find('n1:creditamount').find('n1:amount').get_text(strip=True)
                temp_dict['Transaction Flag'] = 'Credit'
                
            else:
                temp_dict['Transaction Amount'] = general_ledger_line_entry.find('n1:debitamount').find('n1:amount').get_text(strip=True)
                temp_dict['Transaction Flag'] = 'Debit'
            
            # Add current row (temp_dict) to accumulated table (temp_list)
            temp_list.append(temp_dict)
    
    # Convert temp_list to Pandas DataFrame
    # Convert Amount columns from Strings to Floats
    # Combine Balance Amounts and Flags into Calculated Column
    dataset_transactions = pd.DataFrame(temp_list)
    dataset_transactions['Transaction Amount'] = dataset_transactions['Transaction Amount'].astype('float')
    dataset_transactions['Transaction Amount, +/-'] = dataset_transactions[['Transaction Amount','Transaction Flag']].apply(lambda x: x['Transaction Amount'] * multiplier[x['Transaction Flag']], axis = 1)
    
    return dataset_transactions.sort_values(by=['Account ID', 'Transaction Flag'])
    

def extract_accounts(xml_file: type(bs.BeautifulSoup(features="lxml"))) -> pd.DataFrame():
    """
        Extract Accounts Table from SAF-T XML file and export as Pandas DataFrame
        - Combine Debit and Credit Balances into single Balance field
        - Create calculated column from Debit/Credit field and Balance field
        
        Inputs
        --------------------
            xml_file ( Beautiful Soup XML object ): SAF-T file loaded as XML object
        
        Outputs
        --------------------
            dataset_accounts  ( Pandas Dataframe ): Table of Transactions
        
    """
    # Initialise variables - Create temporary dictionary and list
    temp_list = list()
    temp_dict = dict()

    #For each Account in Accounts:
    #   Extract Fields:
    #       - Account ID
    #       - Account Description
    #       - Standard ID
    #       - Account Type
    #       - Account Creation Date
    #       - Opening Balance Amount
    #       - Opening Balance Flag
    #       - Closing Balance Amount
    #       - Closing Balance Flag
    
    for account in xml_file.find('n1:generalledgeraccounts').find_all('n1:account'):
        temp_dict = dict({'Account ID'           : account.find('n1:accountid').get_text(strip=True),
                          'Description'          : account.find('n1:accountdescription').get_text(strip=True),
                          'Standard ID'          : account.find('n1:standardaccountid').get_text(strip=True),
                          'Account Type'         : account.find('n1:accounttype').get_text(strip=True),
                          'Account Creation Date': account.find('n1:accountcreationdate').get_text(strip=True)
                         })
        
        # Determine if the Account Balance is a Debit or a Credit
        # Add Balance Amount and Balance Flag (Debit/ Credit) to temp_dict
        # Opening Balance
        if account.find('n1:openingdebitbalance') is None:
           temp_dict['Opening Balance Amount'] = account.find('n1:openingcreditbalance').get_text(strip=True)
           temp_dict['Opening Balance Flag'] = 'Credit'
        else: 
           temp_dict['Opening Balance Amount'] = account.find('n1:openingdebitbalance').get_text(strip=True)
           temp_dict['Opening Balance Flag'] = 'Debit'
          
        # Closing Balance
        if account.find('n1:closingdebitbalance') is None:
           temp_dict['Closing Balance Amount'] = account.find('n1:closingcreditbalance').get_text(strip=True)
           temp_dict['Closing Balance Flag'] = 'Credit'
        else: 
           temp_dict['Closing Balance Amount'] = account.find('n1:closingdebitbalance').get_text(strip=True)
           temp_dict['Closing Balance Flag'] = 'Debit'
        
        # Add current row (temp_dict) to accumulated table (temp_list)
        temp_list.append(temp_dict)
    
    # Convert temp_list to Pandas DataFrame
    # Convert Amount columns from Strings to Floats
    # Combine Balance Amounts and Flags into Calculated Column
    dataset_accounts = pd.DataFrame(temp_list)
    dataset_accounts['Opening Balance Amount']      = dataset_accounts['Opening Balance Amount'].astype('float')
    dataset_accounts['Opening Balance Amount, +/-'] = dataset_accounts[['Opening Balance Amount','Opening Balance Flag']].apply(lambda x: x['Opening Balance Amount'] * multiplier[x['Opening Balance Flag']], axis = 1)
    dataset_accounts['Closing Balance Amount']      = dataset_accounts['Closing Balance Amount'].astype('float')
    dataset_accounts['Closing Balance Amount, +/-'] = dataset_accounts[['Closing Balance Amount','Closing Balance Flag']].apply(lambda x: x['Closing Balance Amount'] * multiplier[x['Closing Balance Flag']], axis = 1)

    return dataset_accounts.sort_values(by=['Account ID'])
    