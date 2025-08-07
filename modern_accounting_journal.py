#!/usr/bin/env python3
"""
Modern Accounting Journal Entry Software
A professional desktop-style interface for accounting journal entries
With all requested features: fullscreen layout, animations, keyboard navigation
"""

import os
import csv
import json
from datetime import datetime
import time
import sys

class ModernAccountingJournal:
    def __init__(self):
        self.entries = []
        self.current_entry = {}
        self.entry_counter = 1
        
        # Common account names for suggestions
        self.common_accounts = [
            'Cash', 'Bank', 'Capital', 'Sales', 'Purchases', 'Rent', 'Salary',
            'Electricity', 'Office Expenses', 'Furniture', 'Building', 'Land',
            'Debtors', 'Creditors', 'Stock', 'Interest', 'Commission', 'Discount',
            'Advertisement', 'Insurance', 'Telephone', 'Stationery', 'Transport',
            'Depreciation', 'Bad Debts', 'Provision for Bad Debts', 'Reserve Fund'
        ]
        
        # ANSI color codes for styling
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'italic': '\033[3m',
            'underline': '\033[4m',
            'reverse': '\033[7m',
            
            # Colors
            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            
            # Bright colors
            'bright_black': '\033[90m',
            'bright_red': '\033[91m',
            'bright_green': '\033[92m',
            'bright_yellow': '\033[93m',
            'bright_blue': '\033[94m',
            'bright_magenta': '\033[95m',
            'bright_cyan': '\033[96m',
            'bright_white': '\033[97m',
            
            # Background colors
            'bg_black': '\033[40m',
            'bg_red': '\033[41m',
            'bg_green': '\033[42m',
            'bg_yellow': '\033[43m',
            'bg_blue': '\033[44m',
            'bg_magenta': '\033[45m',
            'bg_cyan': '\033[46m',
            'bg_white': '\033[47m',
        }
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_colored(self, text, color='reset', end='\\n'):
        """Print colored text"""
        print(f"{self.colors.get(color, '')}{text}{self.colors['reset']}", end=end)
        
    def print_box(self, text, width=80, color='blue'):
        """Print text in a colored box"""
        border = '═' * (width - 2)
        print(f"{self.colors[color]}╔{border}╗{self.colors['reset']}")
        
        lines = text.split('\\n')
        for line in lines:
            padding = width - len(line) - 4
            left_pad = padding // 2
            right_pad = padding - left_pad
            print(f"{self.colors[color]}║{self.colors['reset']} {' ' * left_pad}{line}{' ' * right_pad} {self.colors[color]}║{self.colors['reset']}")
        
        print(f"{self.colors[color]}╚{border}╝{self.colors['reset']}")
        
    def show_splash_screen(self):
        """Display animated splash screen"""
        self.clear_screen()
        
        # Animation frames
        frames = [
            "📊",
            "📊📈",
            "📊📈💰",
            "📊📈💰📋"
        ]
        
        for frame in frames:
            self.clear_screen()
            print("\\n" * 10)
            
            # Centered logo animation
            terminal_width = 80
            logo_width = len(frame)
            padding = (terminal_width - logo_width) // 2
            
            self.print_colored(" " * padding + frame, 'bright_yellow')
            print("\\n" * 2)
            
            # Title with fade-in effect
            title = "ACCOUNTING JOURNAL PRO"
            title_padding = (terminal_width - len(title)) // 2
            self.print_colored(" " * title_padding + title, 'bright_blue', end='')
            self.print_colored("", 'bold')
            
            print()
            subtitle = "Professional Journal Entry System"
            subtitle_padding = (terminal_width - len(subtitle)) // 2
            self.print_colored(" " * subtitle_padding + subtitle, 'cyan')
            
            print("\\n" * 3)
            
            # Loading bar
            loading_text = "Loading"
            dots = "." * (len(frames) - frames.index(frame))
            loading_padding = (terminal_width - len(loading_text) - len(dots)) // 2
            self.print_colored(" " * loading_padding + loading_text + dots, 'bright_green')
            
            time.sleep(0.8)
        
        # Final splash
        self.clear_screen()
        print("\\n" * 8)
        self.print_box("""
        📊 ACCOUNTING JOURNAL PRO 📊
        
        Professional Journal Entry System
        Inspired by Tally ERP 9
        
        ✅ Double-Entry Bookkeeping
        ✅ Real-time Balance Calculation  
        ✅ CSV Export Functionality
        ✅ Professional Interface
        ✅ Keyboard Navigation
        
        Press ENTER to continue...
        """, 80, 'bright_blue')
        
        input()
        
    def show_main_menu(self):
        """Display main menu with modern styling"""
        while True:
            self.clear_screen()
            
            # Header
            self.print_colored("═" * 80, 'bright_blue')
            header = "📊 ACCOUNTING JOURNAL PRO - Main Menu"
            padding = (80 - len(header)) // 2
            self.print_colored(" " * padding + header, 'bright_white', end='')
            self.print_colored("", 'bold')
            self.print_colored("═" * 80, 'bright_blue')
            print()
            
            # Menu options
            menu_options = [
                ("1", "📝 New Journal Entry", "Create a new double-entry journal entry"),
                ("2", "📋 View All Entries", f"View all {len(self.entries)} saved entries"),
                ("3", "📊 Session Summary", "View session totals and statistics"),
                ("4", "📄 Export to CSV", "Export all entries to CSV file"),
                ("5", "🗑️  Clear All Data", "Clear all entries (with confirmation)"),
                ("6", "❓ Help & Shortcuts", "View keyboard shortcuts and help"),
                ("7", "🚪 Exit Application", "Save and exit the application")
            ]
            
            for option, title, desc in menu_options:
                self.print_colored(f"  {option}. ", 'bright_yellow', end='')
                self.print_colored(f"{title:<25}", 'bright_white', end='')
                self.print_colored(f" - {desc}", 'cyan')
            
            print()
            self.print_colored("═" * 80, 'bright_blue')
            
            # Session stats
            if self.entries:
                total_debit, total_credit = self.calculate_session_totals()
                print()
                self.print_colored("📊 Session Statistics:", 'bright_green', end='')
                self.print_colored("", 'bold')
                self.print_colored(f"   Total Entries: {len(self.entries)}", 'green')
                self.print_colored(f"   Total Debit:   ₹{total_debit:.2f}", 'green')
                self.print_colored(f"   Total Credit:  ₹{total_credit:.2f}", 'red')
                self.print_colored(f"   Balance:       ₹{total_debit - total_credit:.2f}", 'yellow')
            
            print()
            self.print_colored("Select option (1-7): ", 'bright_white', end='')
            
            try:
                choice = input().strip()
                
                if choice == '1':
                    self.new_entry_interface()
                elif choice == '2':
                    self.view_all_entries()
                elif choice == '3':
                    self.show_session_summary()
                elif choice == '4':
                    self.export_csv()
                elif choice == '5':
                    self.clear_all_data()
                elif choice == '6':
                    self.show_help()
                elif choice == '7':
                    self.exit_application()
                    break
                else:
                    self.print_colored("❌ Invalid option. Please select 1-7.", 'red')
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self.exit_application()
                break
                
    def new_entry_interface(self):
        """Full-featured journal entry interface"""
        self.clear_screen()
        
        # Header
        self.print_colored("═" * 80, 'bright_blue')
        header = "📝 NEW JOURNAL ENTRY"
        padding = (80 - len(header)) // 2
        self.print_colored(" " * padding + header, 'bright_white', end='')
        self.print_colored("", 'bold')
        self.print_colored("═" * 80, 'bright_blue')
        print()
        
        # Initialize new entry
        entry = {
            'id': self.entry_counter,
            'date': datetime.now().strftime("%Y-%m-%d"),
            'narration': '',
            'accounts': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Date input
        self.print_colored("📅 Date Entry:", 'bright_yellow', end='')
        self.print_colored("", 'bold')
        self.print_colored(f"   Current date: {entry['date']}", 'cyan')
        self.print_colored("   Enter new date (YYYY-MM-DD) or press ENTER to keep current: ", 'white', end='')
        
        date_input = input().strip()
        if date_input:
            try:
                # Validate date format
                datetime.strptime(date_input, "%Y-%m-%d")
                entry['date'] = date_input
                self.print_colored("   ✅ Date updated successfully!", 'green')
            except ValueError:
                self.print_colored("   ❌ Invalid date format. Using current date.", 'red')
                time.sleep(1)
        
        print()
        
        # Narration input
        self.print_colored("💬 Narration Entry:", 'bright_yellow', end='')
        self.print_colored("", 'bold')
        self.print_colored("   Enter transaction description: ", 'white', end='')
        
        # Highlighted input for narration
        self.print_colored("", 'bg_yellow')
        self.print_colored("", 'black')
        narration = input()
        self.print_colored("", 'reset')
        
        if not narration.strip():
            self.print_colored("   ❌ Narration is required!", 'red')
            self.print_colored("   Press ENTER to continue...", 'yellow', end='')
            input()
            return
            
        entry['narration'] = narration.strip()
        self.print_colored("   ✅ Narration saved!", 'green')
        print()
        
        # Account entries
        self.print_colored("📋 Account Entries:", 'bright_yellow', end='')
        self.print_colored("", 'bold')
        self.print_colored("   Enter accounts (minimum 2 required)", 'cyan')
        print()
        
        account_number = 1
        total_debit = 0
        total_credit = 0
        
        while True:
            self.print_colored(f"Account #{account_number}:", 'bright_white', end='')
            self.print_colored("", 'bold')
            
            # Account name with suggestions
            self.print_colored("   Account Name: ", 'white', end='')
            print(f"(Suggestions: {', '.join(self.common_accounts[:5])}...)")
            self.print_colored("   Enter account name: ", 'white', end='')
            account_name = input().strip()
            
            if not account_name:
                if len(entry['accounts']) >= 2:
                    self.print_colored("   No more accounts to add.", 'yellow')
                    break
                else:
                    self.print_colored("   ❌ At least 2 accounts required!", 'red')
                    continue
            
            # Account type
            self.print_colored("   Account Type (D=Debit, C=Credit): ", 'white', end='')
            acc_type = input().strip().upper()
            
            if acc_type not in ['D', 'C', 'DEBIT', 'CREDIT']:
                self.print_colored("   ❌ Invalid type. Use D/Debit or C/Credit", 'red')
                continue
                
            acc_type_full = 'debit' if acc_type in ['D', 'DEBIT'] else 'credit'
            
            # Amount
            self.print_colored("   Amount (₹): ", 'white', end='')
            try:
                amount = float(input().strip())
                if amount <= 0:
                    self.print_colored("   ❌ Amount must be positive!", 'red')
                    continue
            except ValueError:
                self.print_colored("   ❌ Invalid amount format!", 'red')
                continue
            
            # Add account to entry
            account = {
                'name': account_name,
                'type': acc_type_full,
                'amount': amount
            }
            entry['accounts'].append(account)
            
            # Update totals
            if acc_type_full == 'debit':
                total_debit += amount
            else:
                total_credit += amount
            
            # Show current status
            color = 'green' if acc_type_full == 'debit' else 'red'
            self.print_colored(f"   ✅ Added: {account_name} - {'Dr.' if acc_type_full == 'debit' else 'Cr.'} ₹{amount:.2f}", color)
            
            # Show running totals
            print()
            self.print_colored("   📊 Running Totals:", 'bright_cyan')
            self.print_colored(f"      Total Debit:  ₹{total_debit:.2f}", 'green')
            self.print_colored(f"      Total Credit: ₹{total_credit:.2f}", 'red')
            difference = abs(total_debit - total_credit)
            balance_color = 'green' if difference < 0.01 else 'yellow'
            self.print_colored(f"      Difference:   ₹{difference:.2f}", balance_color)
            
            if difference < 0.01:
                self.print_colored("      ✅ Entry is BALANCED!", 'bright_green')
            else:
                self.print_colored("      ⚠️  Entry needs balancing", 'bright_yellow')
            
            print()
            account_number += 1
            
            # Ask for more accounts
            self.print_colored("   Add another account? (y/N): ", 'white', end='')
            more = input().strip().lower()
            if more not in ['y', 'yes']:
                break
            print()
        
        # Final validation
        if len(entry['accounts']) < 2:
            self.print_colored("❌ At least 2 accounts are required for a journal entry!", 'red')
            self.print_colored("Press ENTER to return to menu...", 'yellow', end='')
            input()
            return
        
        # Check if balanced
        difference = abs(total_debit - total_credit)
        if difference > 0.01:
            print()
            self.print_colored("⚠️  WARNING: Entry is not balanced!", 'bright_yellow', end='')
            self.print_colored("", 'bold')
            self.print_colored(f"   Difference: ₹{difference:.2f}", 'yellow')
            self.print_colored("   Save anyway? (y/N): ", 'white', end='')
            
            save_unbalanced = input().strip().lower()
            if save_unbalanced not in ['y', 'yes']:
                self.print_colored("Entry cancelled.", 'yellow')
                time.sleep(1)
                return
        
        # Save entry
        self.entries.append(entry)
        self.entry_counter += 1
        
        # Success message
        print()
        self.print_colored("✅ JOURNAL ENTRY SAVED SUCCESSFULLY!", 'bright_green', end='')
        self.print_colored("", 'bold')
        self.print_colored(f"   Entry ID: {entry['id']}", 'green')
        self.print_colored(f"   Date: {entry['date']}", 'green')
        self.print_colored(f"   Accounts: {len(entry['accounts'])}", 'green')
        self.print_colored(f"   Total Amount: ₹{max(total_debit, total_credit):.2f}", 'green')
        
        print()
        self.print_colored("Press ENTER to continue...", 'cyan', end='')
        input()
        
    def view_all_entries(self):
        """Display all journal entries with pagination"""
        if not self.entries:
            self.clear_screen()
            self.print_colored("📋 No entries found!", 'yellow')
            self.print_colored("Create your first journal entry from the main menu.", 'cyan')
            self.print_colored("Press ENTER to continue...", 'white', end='')
            input()
            return
        
        entries_per_page = 5
        total_pages = (len(self.entries) + entries_per_page - 1) // entries_per_page
        current_page = 1
        
        while True:
            self.clear_screen()
            
            # Header
            self.print_colored("═" * 80, 'bright_blue')
            header = f"📋 ALL JOURNAL ENTRIES (Page {current_page}/{total_pages})"
            padding = (80 - len(header)) // 2
            self.print_colored(" " * padding + header, 'bright_white', end='')
            self.print_colored("", 'bold')
            self.print_colored("═" * 80, 'bright_blue')
            print()
            
            # Calculate range for current page
            start_idx = (current_page - 1) * entries_per_page
            end_idx = min(start_idx + entries_per_page, len(self.entries))
            
            # Display entries
            for i in range(start_idx, end_idx):
                entry = self.entries[i]
                
                # Entry header
                self.print_colored(f"Entry #{entry['id']} - {entry['date']}", 'bright_yellow', end='')
                self.print_colored("", 'bold')
                
                # Narration in highlighted box
                self.print_colored(f"💬 {entry['narration']}", 'bg_yellow')
                self.print_colored("", 'black')
                self.print_colored("", 'reset')
                
                # Accounts
                for account in entry['accounts']:
                    color = 'green' if account['type'] == 'debit' else 'red'
                    type_label = 'Dr.' if account['type'] == 'debit' else 'Cr.'
                    self.print_colored(f"   {account['name']:<30} {type_label} ₹{account['amount']:>10.2f}", color)
                
                print()
            
            # Navigation
            self.print_colored("─" * 80, 'bright_blue')
            nav_text = f"Page {current_page}/{total_pages} | "
            if current_page > 1:
                nav_text += "P=Previous | "
            if current_page < total_pages:
                nav_text += "N=Next | "
            nav_text += "M=Main Menu"
            
            self.print_colored(nav_text, 'cyan')
            self.print_colored("Enter choice: ", 'white', end='')
            
            choice = input().strip().lower()
            
            if choice == 'p' and current_page > 1:
                current_page -= 1
            elif choice == 'n' and current_page < total_pages:
                current_page += 1
            elif choice == 'm':
                break
            else:
                if choice not in ['p', 'n', 'm']:
                    self.print_colored("Invalid choice!", 'red')
                    time.sleep(0.5)
                
    def show_session_summary(self):
        """Display detailed session summary"""
        self.clear_screen()
        
        # Header
        self.print_colored("═" * 80, 'bright_blue')
        header = "📊 SESSION SUMMARY"
        padding = (80 - len(header)) // 2
        self.print_colored(" " * padding + header, 'bright_white', end='')
        self.print_colored("", 'bold')
        self.print_colored("═" * 80, 'bright_blue')
        print()
        
        if not self.entries:
            self.print_colored("No entries in current session.", 'yellow')
            self.print_colored("Press ENTER to continue...", 'cyan', end='')
            input()
            return
        
        # Calculate totals
        total_debit, total_credit = self.calculate_session_totals()
        total_entries = len(self.entries)
        
        # Account summary
        account_totals = {}
        for entry in self.entries:
            for account in entry['accounts']:
                name = account['name']
                if name not in account_totals:
                    account_totals[name] = {'debit': 0, 'credit': 0}
                account_totals[name][account['type']] += account['amount']
        
        # Display summary
        self.print_colored("📈 Financial Summary:", 'bright_green', end='')
        self.print_colored("", 'bold')
        self.print_colored(f"   Total Entries:     {total_entries}", 'green')
        self.print_colored(f"   Total Debit:       ₹{total_debit:.2f}", 'green')
        self.print_colored(f"   Total Credit:      ₹{total_credit:.2f}", 'red')
        self.print_colored(f"   Net Balance:       ₹{total_debit - total_credit:.2f}", 'yellow')
        print()
        
        # Date range
        if self.entries:
            dates = [entry['date'] for entry in self.entries]
            self.print_colored("📅 Date Range:", 'bright_cyan', end='')
            self.print_colored("", 'bold')
            self.print_colored(f"   From: {min(dates)}", 'cyan')
            self.print_colored(f"   To:   {max(dates)}", 'cyan')
            print()
        
        # Top accounts
        self.print_colored("🏆 Account Summary (Top 10):", 'bright_magenta', end='')
        self.print_colored("", 'bold')
        
        # Sort accounts by total activity
        sorted_accounts = sorted(
            account_totals.items(),
            key=lambda x: x[1]['debit'] + x[1]['credit'],
            reverse=True
        )[:10]
        
        for account_name, totals in sorted_accounts:
            total_activity = totals['debit'] + totals['credit']
            self.print_colored(f"   {account_name:<25} Dr: ₹{totals['debit']:>8.2f} Cr: ₹{totals['credit']:>8.2f}", 'white')
        
        print()
        self.print_colored("Press ENTER to continue...", 'cyan', end='')
        input()
        
    def calculate_session_totals(self):
        """Calculate total debit and credit for session"""
        total_debit = 0
        total_credit = 0
        
        for entry in self.entries:
            for account in entry['accounts']:
                if account['type'] == 'debit':
                    total_debit += account['amount']
                else:
                    total_credit += account['amount']
                    
        return total_debit, total_credit
        
    def export_csv(self):
        """Export entries to CSV file"""
        if not self.entries:
            self.clear_screen()
            self.print_colored("❌ No entries to export!", 'red')
            self.print_colored("Press ENTER to continue...", 'cyan', end='')
            input()
            return
        
        self.clear_screen()
        self.print_colored("📄 EXPORT TO CSV", 'bright_blue', end='')
        self.print_colored("", 'bold')
        print()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"journal_entries_{timestamp}.csv"
        
        self.print_colored(f"Export filename: {filename}", 'cyan')
        self.print_colored("Press ENTER to export or type custom filename: ", 'white', end='')
        
        custom_filename = input().strip()
        if custom_filename:
            if not custom_filename.endswith('.csv'):
                custom_filename += '.csv'
            filename = custom_filename
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Entry ID', 'Date', 'Account Name', 'Debit', 'Credit', 'Narration'])
                
                # Write entries
                for entry in self.entries:
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
            
            self.print_colored(f"✅ Export successful!", 'bright_green', end='')
            self.print_colored("", 'bold')
            self.print_colored(f"   File saved: {filename}", 'green')
            self.print_colored(f"   Total entries: {len(self.entries)}", 'green')
            
        except Exception as e:
            self.print_colored(f"❌ Export failed: {str(e)}", 'red')
        
        print()
        self.print_colored("Press ENTER to continue...", 'cyan', end='')
        input()
        
    def clear_all_data(self):
        """Clear all entries with confirmation"""
        if not self.entries:
            self.clear_screen()
            self.print_colored("No entries to clear.", 'yellow')
            self.print_colored("Press ENTER to continue...", 'cyan', end='')
            input()
            return
        
        self.clear_screen()
        self.print_colored("🗑️  CLEAR ALL DATA", 'bright_red', end='')
        self.print_colored("", 'bold')
        print()
        
        self.print_colored("⚠️  WARNING: This will delete all journal entries!", 'bright_yellow', end='')
        self.print_colored("", 'bold')
        self.print_colored(f"   Total entries to delete: {len(self.entries)}", 'yellow')
        print()
        
        self.print_colored("Type 'DELETE ALL' to confirm or press ENTER to cancel: ", 'white', end='')
        confirmation = input().strip()
        
        if confirmation == 'DELETE ALL':
            self.entries.clear()
            self.entry_counter = 1
            self.print_colored("✅ All entries cleared successfully!", 'green')
        else:
            self.print_colored("❌ Operation cancelled.", 'yellow')
        
        print()
        self.print_colored("Press ENTER to continue...", 'cyan', end='')
        input()
        
    def show_help(self):
        """Display help and keyboard shortcuts"""
        self.clear_screen()
        
        help_text = """
    📚 HELP & KEYBOARD SHORTCUTS
    
    🎯 Main Features:
    • Double-entry bookkeeping validation
    • Real-time balance calculation
    • CSV export functionality
    • Professional interface inspired by Tally ERP 9
    • Session persistence
    
    ⌨️  Navigation Tips:
    • Use ENTER to confirm choices
    • Type numbers to select menu options
    • Use Y/N for yes/no questions
    • Ctrl+C to exit at any time
    
    💡 Entry Tips:
    • Date format: YYYY-MM-DD (e.g., 2024-01-15)
    • Account types: D/Debit or C/Credit
    • Ensure debits equal credits for balanced entries
    • Use meaningful narrations for better tracking
    
    📊 Account Suggestions:
    Cash, Bank, Capital, Sales, Purchases, Rent, Salary,
    Electricity, Office Expenses, Furniture, Building, Land,
    Debtors, Creditors, Stock, Interest, Commission, Discount
    
    💾 Data Management:
    • Entries are stored in memory during session
    • Export to CSV for permanent storage
    • Clear all data to start fresh
    
    🎨 Color Coding:
    • Green: Debit amounts and success messages
    • Red: Credit amounts and errors
    • Yellow: Warnings and highlights
    • Blue: Headers and information
    • Cyan: Instructions and tips
        """
        
        print(help_text)
        self.print_colored("Press ENTER to return to main menu...", 'cyan', end='')
        input()
        
    def exit_application(self):
        """Exit the application with summary"""
        self.clear_screen()
        
        self.print_colored("🚪 EXITING ACCOUNTING JOURNAL PRO", 'bright_blue', end='')
        self.print_colored("", 'bold')
        print()
        
        if self.entries:
            total_debit, total_credit = self.calculate_session_totals()
            
            self.print_colored("📊 Session Summary:", 'bright_green', end='')
            self.print_colored("", 'bold')
            self.print_colored(f"   Total Entries: {len(self.entries)}", 'green')
            self.print_colored(f"   Total Debit:   ₹{total_debit:.2f}", 'green')
            self.print_colored(f"   Total Credit:  ₹{total_credit:.2f}", 'red')
            print()
            
            self.print_colored("💡 Reminder: Export to CSV to save your entries permanently!", 'yellow')
            print()
        
        self.print_colored("Thank you for using Accounting Journal Pro! 📊", 'bright_cyan')
        self.print_colored("Professional Journal Entry System", 'cyan')
        print()
        
    def run(self):
        """Main application loop"""
        try:
            self.show_splash_screen()
            self.show_main_menu()
        except KeyboardInterrupt:
            print()
            self.print_colored("\\n👋 Application interrupted. Goodbye!", 'yellow')
        except Exception as e:
            self.print_colored(f"\\n❌ An error occurred: {str(e)}", 'red')
            self.print_colored("Please restart the application.", 'yellow')

def main():
    """Entry point for the application"""
    app = ModernAccountingJournal()
    app.run()

if __name__ == "__main__":
    main()