import os
import csv
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
from io import StringIO

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "accounting_journal_secret_key_2024")

# Initialize session data structure
def init_session():
    if 'entries' not in session:
        session['entries'] = []
    if 'entry_counter' not in session:
        session['entry_counter'] = 1

@app.route('/')
def index():
    init_session()
    
    # Calculate running totals
    total_debit = 0
    total_credit = 0
    
    for entry in session['entries']:
        for account in entry.get('accounts', []):
            if account.get('type') == 'debit':
                total_debit += float(account.get('amount', 0))
            else:
                total_credit += float(account.get('amount', 0))
    
    return render_template('index.html', 
                         entries=session['entries'], 
                         total_debit=total_debit,
                         total_credit=total_credit,
                         today_date=datetime.now().strftime('%Y-%m-%d'))

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
        
        # Filter out empty accounts
        accounts = []
        total_debit = 0
        total_credit = 0
        
        for i in range(len(account_names)):
            if i < len(account_types) and i < len(account_amounts):
                name = account_names[i].strip()
                acc_type = account_types[i]
                amount_str = account_amounts[i].strip()
                
                if name and amount_str:
                    try:
                        amount = float(amount_str)
                        if amount > 0:
                            accounts.append({
                                'name': name,
                                'type': acc_type,
                                'amount': amount
                            })
                            if acc_type == 'debit':
                                total_debit += amount
                            else:
                                total_credit += amount
                    except ValueError:
                        flash(f'Invalid amount for account {name}', 'error')
                        return redirect(url_for('index'))
        
        if not accounts:
            flash('At least one account entry is required!', 'error')
            return redirect(url_for('index'))
        
        if abs(total_debit - total_credit) > 0.01:  # Allow small floating point differences
            flash(f'Entry is not balanced! Debit: {total_debit:.2f}, Credit: {total_credit:.2f}', 'error')
            return redirect(url_for('index'))
        
        # Create new entry
        new_entry = {
            'id': session['entry_counter'],
            'date': entry_date,
            'narration': narration,
            'accounts': accounts,
            'timestamp': datetime.now().isoformat()
        }
        
        session['entries'].append(new_entry)
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
    session['entries'] = [entry for entry in session['entries'] if entry['id'] != entry_id]
    session.modified = True
    
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/export_csv')
def export_csv():
    init_session()
    
    if not session['entries']:
        flash('No entries to export!', 'error')
        return redirect(url_for('index'))
    
    # Create CSV content
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Entry ID', 'Date', 'Account Name', 'Debit', 'Credit', 'Narration'])
    
    # Write entries
    for entry in session['entries']:
        for account in entry['accounts']:
            debit_amount = account['amount'] if account['type'] == 'debit' else ''
            credit_amount = account['amount'] if account['type'] == 'credit' else ''
            
            writer.writerow([
                entry['id'],
                entry['date'],
                account['name'],
                debit_amount,
                credit_amount,
                entry['narration']
            ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=journal_entries_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/clear_session')
def clear_session():
    session.clear()
    flash('All entries cleared!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
