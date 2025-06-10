from statements.all_imports_for_diff_checker import *
from company_mapper import *


def missing_doc_and_wrong_amount(bc_balance=dict, vendor_balance=dict, obj=object):
    missing_documents = {}
    wrong_amounts = {}
    for inv, value in vendor_balance.items():
        if str(inv) not in bc_balance:
            missing_documents[inv] = value
            continue
        
        diff = float(value) + float(bc_balance[str(inv)])

        if abs(diff) > 3:
            wrong_amounts[inv] = diff

    all_numbers = find_account_number()
    print(f"Company name: {obj.__class__.__name__.replace('Model', '')}")
    print(f"Account No. in BC: {', '.join(find_account_number())}")
    print('===================================')
    print(f"All missing documents:")
    if not missing_documents:
        print('There are no missing invoices')
    else:
        print('\n'.join(f'Invoice {inv}, amount: {amount}' for inv, amount in missing_documents.items()))
    
    print('===================================')
    print(f"All wrong invoices:")
    if not wrong_amounts:
        print('There are no wrong invoices')
    else:
        print('\n'.join(f'Invoice {inv}, amount: {amount}' for inv, amount in wrong_amounts.items()))


# missing_doc_and_wrong_amount(bc_balance(), company_mapper["ah_fragt"].vendor_balance(), company_mapper["ah_fragt"])
