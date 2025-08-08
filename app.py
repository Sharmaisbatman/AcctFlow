import os
import csv
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash, jsonify
from io import StringIO
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "accounting_pro_secret_key_2024")

# Context processor to provide common template variables
@app.context_processor
def utility_processor():
    def format_date(format_str='%B %d, %Y'):
        return datetime.now().strftime(format_str)
    return dict(format_date=format_date)

# Initialize session data structure
def init_session():
    if 'journal_entries' not in session:
        session['journal_entries'] = []
    if 'entry_counter' not in session:
        session['entry_counter'] = 1

@app.route('/')
def index():
    init_session()
    return render_template('index.html', 
                         entries=session['journal_entries'],
                         today_date=datetime.now().strftime('%Y-%m-%d'))

@app.route('/journal')
def journal():
    init_session()
    
    # Calculate totals for each entry and overall
    for entry in session['journal_entries']:
        entry_debit = sum(acc['amount'] for acc in entry['accounts'] if acc['type'] == 'debit')
        entry_credit = sum(acc['amount'] for acc in entry['accounts'] if acc['type'] == 'credit')
        entry['total_debit'] = entry_debit
        entry['total_credit'] = entry_credit
        entry['is_balanced'] = abs(entry_debit - entry_credit) < 0.01
    
    # Calculate grand totals
    grand_debit = sum(entry.get('total_debit', 0) for entry in session['journal_entries'])
    grand_credit = sum(entry.get('total_credit', 0) for entry in session['journal_entries'])
    
    return render_template('journal.html', 
                         entries=session['journal_entries'],
                         grand_debit=grand_debit,
                         grand_credit=grand_credit)

@app.route('/ledgers')
def ledgers():
    init_session()
    
    # Generate ledgers from journal entries
    ledgers = defaultdict(lambda: {'debit_entries': [], 'credit_entries': [], 'debit_total': 0, 'credit_total': 0})
    
    for entry in session['journal_entries']:
        for account in entry['accounts']:
            account_name = account['name']
            ledger_entry = {
                'date': entry['date'],
                'particulars': f"To {account['contra_account']}" if account['type'] == 'debit' else f"By {account['contra_account']}",
                'jf': f"J{entry['id']}",
                'amount': account['amount']
            }
            
            if account['type'] == 'debit':
                ledgers[account_name]['debit_entries'].append(ledger_entry)
                ledgers[account_name]['debit_total'] += account['amount']
            else:
                ledgers[account_name]['credit_entries'].append(ledger_entry)
                ledgers[account_name]['credit_total'] += account['amount']
    
    # Sort ledgers alphabetically
    sorted_ledgers = dict(sorted(ledgers.items()))
    
    return render_template('ledgers.html', ledgers=sorted_ledgers)

@app.route('/trial_balance')
def trial_balance():
    init_session()
    
    # Generate trial balance - shows net balance of each account
    account_balances = defaultdict(lambda: {'debit_total': 0, 'credit_total': 0, 'net_balance': 0})
    
    # Sum up all debits and credits for each account
    for entry in session['journal_entries']:
        for account in entry['accounts']:
            account_name = account['name']
            amount = account['amount']
            
            if account['type'] == 'debit':
                account_balances[account_name]['debit_total'] += amount
            else:
                account_balances[account_name]['credit_total'] += amount
    
    # Calculate net balance and classify for trial balance
    trial_balance_accounts = []
    total_debit_balances = 0
    total_credit_balances = 0
    
    for account_name, balance_info in sorted(account_balances.items()):
        debit_total = balance_info['debit_total']
        credit_total = balance_info['credit_total']
        net_balance = debit_total - credit_total
        
        # Only include accounts with non-zero balances
        if abs(net_balance) > 0.01:
            if net_balance > 0:
                # Account has net debit balance
                trial_balance_accounts.append({
                    'account': account_name,
                    'debit_balance': net_balance,
                    'credit_balance': 0
                })
                total_debit_balances += net_balance
            else:
                # Account has net credit balance
                trial_balance_accounts.append({
                    'account': account_name,
                    'debit_balance': 0,
                    'credit_balance': abs(net_balance)
                })
                total_credit_balances += abs(net_balance)
    
    # Check if trial balance is balanced
    is_balanced = abs(total_debit_balances - total_credit_balances) < 0.01
    
    return render_template('trial_balance.html', 
                         trial_balance=trial_balance_accounts,
                         total_debit=total_debit_balances,
                         total_credit=total_credit_balances,
                         is_balanced=is_balanced)

@app.route('/profit_loss')
def profit_loss():
    init_session()
    
    # GAAP-based P&L Account Classifications
    # Revenue keywords - these are typically CREDIT balance accounts
    revenue_keywords = [
        'sales', 'revenue', 'income', 'service revenue', 'consulting income', 'fees earned',
        'interest received', 'rent received', 'commission received', 'dividend received',
        'discount received', 'gain on sale', 'other income', 'miscellaneous income',
        'royalty income', 'rental income', 'service fees', 'professional fees'
    ]
    
    # Expense keywords - these are typically DEBIT balance accounts
    expense_keywords = [
        # Cost of Goods Sold
        'cost of goods sold', 'cogs', 'cost of sales', 'purchases', 'materials', 'inventory',
        
        # Operating Expenses
        'salary', 'salaries', 'wages', 'payroll', 'benefits', 'bonus', 'commission paid',
        'rent expense', 'office rent', 'utilities', 'electricity', 'water', 'gas',
        'telephone', 'internet', 'mobile', 'communication',
        'office expense', 'supplies', 'stationery', 'printing', 'postage',
        'advertising', 'marketing', 'promotion', 'publicity',
        'travel', 'transport', 'fuel', 'vehicle expense', 'conveyance',
        'insurance expense', 'professional fees', 'legal fees', 'audit fees',
        'consultant fees', 'bank charges', 'interest expense', 'loan interest',
        'repairs', 'maintenance', 'cleaning', 'security',
        'depreciation', 'amortization', 'bad debts', 'doubtful debts',
        'training', 'conference', 'subscription', 'license fee',
        'tax expense', 'penalty', 'fine', 'loss', 'miscellaneous expense'
    ]
    
    # Calculate net balances for each account
    account_balances = defaultdict(lambda: {'debit_total': 0, 'credit_total': 0, 'net_balance': 0})
    
    for entry in session['journal_entries']:
        for account in entry['accounts']:
            account_name = account['name']
            amount = account['amount']
            
            if account['type'] == 'debit':
                account_balances[account_name]['debit_total'] += amount
            else:
                account_balances[account_name]['credit_total'] += amount
    
    # Calculate net balance for each account
    for account_name in account_balances:
        balance_info = account_balances[account_name]
        balance_info['net_balance'] = balance_info['debit_total'] - balance_info['credit_total']
    
    # Classify accounts for P&L based on GAAP principles
    revenue_accounts = []
    expense_accounts = []
    
    for account_name, balance_info in account_balances.items():
        account_lower = account_name.lower()
        net_balance = balance_info['net_balance']
        
        # Revenue Classification: Credit balance accounts with revenue keywords
        if any(keyword in account_lower for keyword in revenue_keywords):
            if net_balance < 0:  # Credit balance (normal for revenue)
                revenue_accounts.append({
                    'account': account_name, 
                    'amount': abs(net_balance)  # Show as positive amount
                })
        
        # Expense Classification: Debit balance accounts with expense keywords
        elif any(keyword in account_lower for keyword in expense_keywords):
            if net_balance > 0:  # Debit balance (normal for expenses)
                expense_accounts.append({
                    'account': account_name,
                    'amount': net_balance
                })
    
    # Calculate totals
    total_revenue = sum(acc['amount'] for acc in revenue_accounts)
    total_expenses = sum(acc['amount'] for acc in expense_accounts)
    net_profit = total_revenue - total_expenses
    
    return render_template('profit_loss.html',
                         expenses=expense_accounts,
                         income=revenue_accounts,
                         total_expenses=total_expenses,
                         total_income=total_revenue,
                         net_profit=net_profit)

@app.route('/balance_sheet')
def balance_sheet():
    init_session()
    
    # GAAP-based Balance Sheet Classifications
    # Current Assets (converted to cash within 1 year)
    current_asset_keywords = [
        'cash', 'petty cash', 'bank', 'checking', 'savings', 'money market',
        'accounts receivable', 'trade receivables', 'notes receivable', 'debtors',
        'inventory', 'stock', 'merchandise', 'raw materials', 'finished goods',
        'prepaid expenses', 'prepaid rent', 'prepaid insurance', 'supplies',
        'short-term investment', 'marketable securities'
    ]
    
    # Non-Current Assets (long-term assets)
    non_current_asset_keywords = [
        'land', 'building', 'equipment', 'machinery', 'furniture', 'fixtures',
        'vehicle', 'motor car', 'truck', 'computer', 'laptop', 'software',
        'patent', 'trademark', 'goodwill', 'long-term investment',
        'property', 'plant', 'intangible', 'fixed asset'
    ]
    
    # Current Liabilities (due within 1 year)
    current_liability_keywords = [
        'accounts payable', 'trade payables', 'notes payable', 'creditors',
        'accrued expenses', 'accrued liabilities', 'wages payable', 'salary payable',
        'interest payable', 'tax payable', 'short-term loan', 'credit card',
        'overdraft', 'current portion', 'unearned revenue'
    ]
    
    # Non-Current Liabilities (due after 1 year)
    non_current_liability_keywords = [
        'long-term loan', 'mortgage', 'bonds payable', 'deferred tax',
        'pension liability', 'long-term debt'
    ]
    
    # Equity accounts
    equity_keywords = [
        'capital', 'owner capital', 'share capital', 'common stock', 'preferred stock',
        'additional paid-in capital', 'retained earnings', 'reserve', 'surplus',
        'drawing', 'owner drawing', 'dividends', 'treasury stock'
    ]
    
    # Calculate net balances for each account
    account_balances = defaultdict(lambda: {'debit_total': 0, 'credit_total': 0, 'net_balance': 0})
    
    for entry in session['journal_entries']:
        for account in entry['accounts']:
            account_name = account['name']
            amount = account['amount']
            
            if account['type'] == 'debit':
                account_balances[account_name]['debit_total'] += amount
            else:
                account_balances[account_name]['credit_total'] += amount
    
    # Calculate net balance for each account
    for account_name in account_balances:
        balance_info = account_balances[account_name]
        balance_info['net_balance'] = balance_info['debit_total'] - balance_info['credit_total']
    
    # Classify accounts based on GAAP principles
    current_assets = []
    non_current_assets = []
    current_liabilities = []
    non_current_liabilities = []
    equity_accounts = []
    
    for account_name, balance_info in account_balances.items():
        account_lower = account_name.lower()
        net_balance = balance_info['net_balance']
        
        # Skip P&L accounts (revenue/expense) - they belong in Income Statement
        revenue_keywords = ['sales', 'revenue', 'income', 'interest received', 'rent received']
        expense_keywords = ['expense', 'salary', 'rent expense', 'cost of goods sold']
        
        is_pnl_account = (any(keyword in account_lower for keyword in revenue_keywords) or 
                         any(keyword in account_lower for keyword in expense_keywords))
        
        if is_pnl_account:
            continue  # Skip P&L accounts in Balance Sheet
        
        # Current Assets: Debit balance accounts
        if any(keyword in account_lower for keyword in current_asset_keywords):
            if net_balance > 0:
                current_assets.append({'account': account_name, 'amount': net_balance})
        
        # Non-Current Assets: Debit balance accounts
        elif any(keyword in account_lower for keyword in non_current_asset_keywords):
            if net_balance > 0:
                non_current_assets.append({'account': account_name, 'amount': net_balance})
        
        # Current Liabilities: Credit balance accounts
        elif any(keyword in account_lower for keyword in current_liability_keywords):
            if net_balance < 0:
                current_liabilities.append({'account': account_name, 'amount': abs(net_balance)})
        
        # Non-Current Liabilities: Credit balance accounts
        elif any(keyword in account_lower for keyword in non_current_liability_keywords):
            if net_balance < 0:
                non_current_liabilities.append({'account': account_name, 'amount': abs(net_balance)})
        
        # Equity: Mostly credit balance (except drawings)
        elif any(keyword in account_lower for keyword in equity_keywords):
            if 'drawing' in account_lower:
                # Drawings have debit balance and reduce equity
                if net_balance > 0:
                    equity_accounts.append({'account': account_name, 'amount': -net_balance})
            else:
                # Other equity accounts have credit balance
                if net_balance < 0:
                    equity_accounts.append({'account': account_name, 'amount': abs(net_balance)})
    
    # Combine assets
    all_assets = current_assets + non_current_assets
    all_liabilities = current_liabilities + non_current_liabilities
    
    # Calculate totals
    total_assets = sum(asset['amount'] for asset in all_assets)
    total_liabilities = sum(liability['amount'] for liability in all_liabilities)
    total_equity = sum(eq['amount'] for eq in equity_accounts)
    
    # Add net profit from P&L to equity (basic approach)
    # In a real system, this would be calculated from the P&L statement
    retained_earnings = total_assets - total_liabilities - total_equity
    if abs(retained_earnings) > 0.01:
        equity_accounts.append({'account': 'Retained Earnings', 'amount': retained_earnings})
        total_equity += retained_earnings
    
    return render_template('balance_sheet.html',
                         assets=all_assets,
                         liabilities=all_liabilities,
                         equity=equity_accounts,
                         total_assets=total_assets,
                         total_liabilities=total_liabilities,
                         total_equity=total_equity)

@app.route('/add_entry', methods=['POST'])
def add_entry():
    init_session()
    
    try:
        # Get form data
        entry_date = request.form.get('entry_date')
        narration = request.form.get('narration', '').strip()
        
        # Get account data
        account_names = request.form.getlist('account_name')
        account_types = request.form.getlist('account_type')
        account_amounts = request.form.getlist('account_amount')
        
        # Validate entry
        if not entry_date or not narration:
            flash('Date and narration are required!', 'error')
            return redirect(url_for('index'))
        
        # Process accounts
        accounts = []
        total_debit = 0
        total_credit = 0
        debit_accounts = []
        credit_accounts = []
        
        for i in range(len(account_names)):
            if i < len(account_types) and i < len(account_amounts):
                name = account_names[i].strip()
                acc_type = account_types[i]
                amount_str = account_amounts[i].strip()
                
                if name and amount_str:
                    try:
                        amount = float(amount_str)
                        if amount > 0:
                            if acc_type == 'debit':
                                debit_accounts.append(name)
                                total_debit += amount
                            else:
                                credit_accounts.append(name)
                                total_credit += amount
                            
                            accounts.append({
                                'name': name,
                                'type': acc_type,
                                'amount': amount
                            })
                    except ValueError:
                        flash(f'Invalid amount for account {name}', 'error')
                        return redirect(url_for('index'))
        
        if not accounts:
            flash('At least one account entry is required!', 'error')
            return redirect(url_for('index'))
        
        if len(accounts) < 2:
            flash('At least two accounts are required for a journal entry!', 'error')
            return redirect(url_for('index'))
        
        # Check if balanced
        if abs(total_debit - total_credit) > 0.01:
            flash(f'Entry is not balanced! Debit: ₹{total_debit:.2f}, Credit: ₹{total_credit:.2f}', 'error')
            return redirect(url_for('index'))
        
        # Add contra account information for ledger generation
        for account in accounts:
            if account['type'] == 'debit':
                account['contra_account'] = ' & '.join(credit_accounts)
            else:
                account['contra_account'] = ' & '.join(debit_accounts)
        
        # Create new entry
        new_entry = {
            'id': session['entry_counter'],
            'date': entry_date,
            'narration': narration,
            'accounts': accounts,
            'timestamp': datetime.now().isoformat()
        }
        
        session['journal_entries'].append(new_entry)
        session['entry_counter'] += 1
        session.modified = True
        
        flash('Journal entry added successfully!', 'success')
        
    except Exception as e:
        logging.error(f"Error adding entry: {str(e)}")
        flash('An error occurred while adding the entry. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete_entry/<int:entry_id>')
def delete_entry(entry_id):
    init_session()
    
    # Find and remove entry
    session['journal_entries'] = [entry for entry in session['journal_entries'] if entry['id'] != entry_id]
    session.modified = True
    
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('journal'))

@app.route('/export_csv/<report_type>')
def export_csv(report_type):
    init_session()
    
    if not session['journal_entries'] and report_type != 'sample':
        flash('No entries to export!', 'error')
        return redirect(url_for('index'))
    
    # Create CSV content based on report type
    output = StringIO()
    writer = csv.writer(output)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if report_type == 'journal':
        filename = f"journal_entries_{timestamp}.csv"
        writer.writerow(['Date', 'Account Name', 'Debit', 'Credit', 'Narration'])
        
        for entry in session['journal_entries']:
            for i, account in enumerate(entry['accounts']):
                debit_amount = account['amount'] if account['type'] == 'debit' else ''
                credit_amount = account['amount'] if account['type'] == 'credit' else ''
                narration = entry['narration'] if i == 0 else ''
                
                writer.writerow([
                    entry['date'] if i == 0 else '',
                    account['name'],
                    debit_amount,
                    credit_amount,
                    narration
                ])
            writer.writerow(['', '', '', '', ''])  # Empty row between entries
    
    elif report_type == 'trial_balance':
        filename = f"trial_balance_{timestamp}.csv"
        
        # Generate trial balance data (similar to trial_balance route)
        accounts = defaultdict(lambda: {'debit_balance': 0, 'credit_balance': 0})
        
        for entry in session['journal_entries']:
            for account in entry['accounts']:
                account_name = account['name']
                if account['type'] == 'debit':
                    accounts[account_name]['debit_balance'] += account['amount']
                else:
                    accounts[account_name]['credit_balance'] += account['amount']
        
        writer.writerow(['Account Name', 'Debit Balance', 'Credit Balance'])
        
        total_debit = 0
        total_credit = 0
        
        for account_name, balances in sorted(accounts.items()):
            net_debit = balances['debit_balance'] - balances['credit_balance']
            net_credit = balances['credit_balance'] - balances['debit_balance']
            
            if net_debit > 0:
                writer.writerow([account_name, f"{net_debit:.2f}", ""])
                total_debit += net_debit
            elif net_credit > 0:
                writer.writerow([account_name, "", f"{net_credit:.2f}"])
                total_credit += net_credit
        
        writer.writerow(['TOTAL', f"{total_debit:.2f}", f"{total_credit:.2f}"])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

@app.route('/clear_session')
def clear_session():
    session.clear()
    flash('All entries cleared!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)