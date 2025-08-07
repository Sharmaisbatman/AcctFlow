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
    
    # Generate trial balance from journal entries
    accounts = defaultdict(lambda: {'debit_balance': 0, 'credit_balance': 0})
    
    for entry in session['journal_entries']:
        for account in entry['accounts']:
            account_name = account['name']
            if account['type'] == 'debit':
                accounts[account_name]['debit_balance'] += account['amount']
            else:
                accounts[account_name]['credit_balance'] += account['amount']
    
    # Calculate net balances
    trial_balance = []
    total_debit = 0
    total_credit = 0
    
    for account_name, balances in sorted(accounts.items()):
        net_debit = balances['debit_balance'] - balances['credit_balance']
        net_credit = balances['credit_balance'] - balances['debit_balance']
        
        if net_debit > 0:
            trial_balance.append({
                'account': account_name,
                'debit_balance': net_debit,
                'credit_balance': 0
            })
            total_debit += net_debit
        elif net_credit > 0:
            trial_balance.append({
                'account': account_name,
                'debit_balance': 0,
                'credit_balance': net_credit
            })
            total_credit += net_credit
    
    return render_template('trial_balance.html', 
                         trial_balance=trial_balance,
                         total_debit=total_debit,
                         total_credit=total_credit,
                         is_balanced=abs(total_debit - total_credit) < 0.01)

@app.route('/profit_loss')
def profit_loss():
    init_session()
    
    # Account classifications for P&L
    expense_keywords = ['expense', 'rent', 'salary', 'salaries', 'electricity', 'telephone', 'insurance', 
                       'depreciation', 'interest', 'commission', 'advertising', 'office', 'transport',
                       'repairs', 'maintenance', 'audit', 'legal', 'bad debts', 'loss']
    
    income_keywords = ['sales', 'revenue', 'income', 'fees earned', 'interest received', 'rent received',
                      'commission received', 'dividend', 'discount received', 'profit']
    
    # Calculate account balances
    accounts = defaultdict(lambda: {'debit_balance': 0, 'credit_balance': 0})
    
    for entry in session['journal_entries']:
        for account in entry['accounts']:
            account_name = account['name']
            if account['type'] == 'debit':
                accounts[account_name]['debit_balance'] += account['amount']
            else:
                accounts[account_name]['credit_balance'] += account['amount']
    
    # Classify accounts
    expenses = []
    income = []
    
    for account_name, balances in accounts.items():
        net_balance = balances['debit_balance'] - balances['credit_balance']
        account_lower = account_name.lower()
        
        # Check if it's an expense account (typically debit balance)
        if any(keyword in account_lower for keyword in expense_keywords) and net_balance > 0:
            expenses.append({'account': account_name, 'amount': net_balance})
        
        # Check if it's an income account (typically credit balance)
        elif any(keyword in account_lower for keyword in income_keywords) and net_balance < 0:
            income.append({'account': account_name, 'amount': abs(net_balance)})
    
    total_expenses = sum(exp['amount'] for exp in expenses)
    total_income = sum(inc['amount'] for inc in income)
    net_profit = total_income - total_expenses
    
    return render_template('profit_loss.html',
                         expenses=expenses,
                         income=income,
                         total_expenses=total_expenses,
                         total_income=total_income,
                         net_profit=net_profit)

@app.route('/balance_sheet')
def balance_sheet():
    init_session()
    
    # Account classifications for Balance Sheet
    asset_keywords = ['cash', 'bank', 'accounts receivable', 'inventory', 'stock', 'equipment', 
                     'furniture', 'building', 'land', 'machinery', 'vehicle', 'investment',
                     'prepaid', 'supplies', 'debtors']
    
    liability_keywords = ['accounts payable', 'creditors', 'notes payable', 'loan', 'mortgage',
                         'accrued', 'unearned', 'tax payable', 'interest payable']
    
    equity_keywords = ['capital', 'retained earnings', 'drawing', 'equity', 'stock']
    
    # Calculate account balances
    accounts = defaultdict(lambda: {'debit_balance': 0, 'credit_balance': 0})
    
    for entry in session['journal_entries']:
        for account in entry['accounts']:
            account_name = account['name']
            if account['type'] == 'debit':
                accounts[account_name]['debit_balance'] += account['amount']
            else:
                accounts[account_name]['credit_balance'] += account['amount']
    
    # Classify accounts
    assets = []
    liabilities = []
    equity = []
    
    for account_name, balances in accounts.items():
        net_balance = balances['debit_balance'] - balances['credit_balance']
        account_lower = account_name.lower()
        
        # Assets (typically debit balance)
        if any(keyword in account_lower for keyword in asset_keywords):
            if net_balance > 0:
                assets.append({'account': account_name, 'amount': net_balance})
        
        # Liabilities (typically credit balance)
        elif any(keyword in account_lower for keyword in liability_keywords):
            if net_balance < 0:
                liabilities.append({'account': account_name, 'amount': abs(net_balance)})
        
        # Equity (typically credit balance, but drawings are debit)
        elif any(keyword in account_lower for keyword in equity_keywords):
            if 'drawing' in account_lower and net_balance > 0:
                equity.append({'account': account_name, 'amount': -net_balance})  # Drawings reduce equity
            elif 'drawing' not in account_lower and net_balance < 0:
                equity.append({'account': account_name, 'amount': abs(net_balance)})
    
    # Calculate net profit from P&L and add to equity
    # (This is a simplified approach - in practice, this would come from the P&L statement)
    
    total_assets = sum(asset['amount'] for asset in assets)
    total_liabilities = sum(liability['amount'] for liability in liabilities)
    total_equity = sum(eq['amount'] for eq in equity)
    
    # Add retained earnings to balance the equation
    retained_earnings = total_assets - total_liabilities - total_equity
    if abs(retained_earnings) > 0.01:
        equity.append({'account': 'Retained Earnings', 'amount': retained_earnings})
        total_equity += retained_earnings
    
    return render_template('balance_sheet.html',
                         assets=assets,
                         liabilities=liabilities,
                         equity=equity,
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