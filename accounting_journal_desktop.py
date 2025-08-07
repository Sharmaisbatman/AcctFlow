#!/usr/bin/env python3
"""
Modern Accounting Journal Entry Software
Built with CustomTkinter for professional desktop experience
Inspired by Tally ERP 9 with modern enhancements
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import csv
import json
from datetime import datetime
import os
import threading
import time

# Set appearance mode and default color theme
ctk.set_appearance_mode("light")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ModernAccountingJournal:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Accounting Journal Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Center the window
        self.center_window()
        
        # Data storage
        self.entries = []
        self.current_entry_accounts = []
        self.entry_counter = 1
        
        # Common account names for autocomplete
        self.common_accounts = [
            'Cash', 'Bank', 'Capital', 'Sales', 'Purchases', 'Rent', 'Salary',
            'Electricity', 'Office Expenses', 'Furniture', 'Building', 'Land',
            'Debtors', 'Creditors', 'Stock', 'Interest', 'Commission', 'Discount',
            'Advertisement', 'Insurance', 'Telephone', 'Stationery', 'Transport',
            'Depreciation', 'Bad Debts', 'Provision for Bad Debts', 'Reserve Fund'
        ]
        
        # Color scheme
        self.colors = {
            'primary': '#1e3c72',
            'secondary': '#2a5298',
            'accent': '#ffd700',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'debit': '#28a745',
            'credit': '#dc3545',
            'narration': '#fff9c4'
        }
        
        # Create splash screen first
        self.create_splash_screen()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_splash_screen(self):
        """Create animated splash screen"""
        # Create splash window
        self.splash = ctk.CTkToplevel()
        self.splash.title("")
        self.splash.geometry("600x400")
        self.splash.resizable(False, False)
        
        # Center splash screen
        self.splash.update_idletasks()
        x = (self.splash.winfo_screenwidth() // 2) - (300)
        y = (self.splash.winfo_screenheight() // 2) - (200)
        self.splash.geometry(f'600x400+{x}+{y}')
        
        # Remove window decorations
        self.splash.overrideredirect(True)
        
        # Create gradient-like background
        splash_frame = ctk.CTkFrame(self.splash, fg_color=self.colors['primary'])
        splash_frame.pack(fill="both", expand=True)
        
        # Logo/Icon (using text as icon)
        logo_label = ctk.CTkLabel(
            splash_frame,
            text="📊",
            font=ctk.CTkFont(size=80),
            text_color=self.colors['accent']
        )
        logo_label.pack(pady=(80, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            splash_frame,
            text="Accounting Journal Pro",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=10)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            splash_frame,
            text="Professional Journal Entry System",
            font=ctk.CTkFont(size=16),
            text_color="lightgray"
        )
        subtitle_label.pack(pady=5)
        
        # Loading bar
        self.progress_bar = ctk.CTkProgressBar(
            splash_frame,
            width=300,
            height=8,
            progress_color=self.colors['accent']
        )
        self.progress_bar.pack(pady=(40, 20))
        self.progress_bar.set(0)
        
        # Loading text
        self.loading_label = ctk.CTkLabel(
            splash_frame,
            text="Initializing...",
            font=ctk.CTkFont(size=12),
            text_color="lightgray"
        )
        self.loading_label.pack()
        
        # Start loading animation
        self.animate_splash()
        
    def animate_splash(self):
        """Animate splash screen loading"""
        loading_steps = [
            "Initializing...",
            "Loading Components...",
            "Setting up Database...",
            "Preparing Interface...",
            "Almost Ready...",
            "Welcome!"
        ]
        
        def update_progress():
            for i, step in enumerate(loading_steps):
                progress = (i + 1) / len(loading_steps)
                self.progress_bar.set(progress)
                self.loading_label.configure(text=step)
                self.splash.update()
                time.sleep(0.5)
            
            # Fade out effect
            for alpha in range(10, 0, -1):
                self.splash.attributes('-alpha', alpha / 10)
                time.sleep(0.05)
            
            self.splash.destroy()
            self.create_main_interface()
            
            # Fade in main window
            self.root.attributes('-alpha', 0)
            self.root.deiconify()
            for alpha in range(0, 11):
                self.root.attributes('-alpha', alpha / 10)
                time.sleep(0.03)
        
        # Run animation in separate thread
        threading.Thread(target=update_progress, daemon=True).start()
        
    def create_main_interface(self):
        """Create the main application interface"""
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Create header
        self.create_header()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        
        # Setup keyboard bindings
        self.setup_keyboard_navigation()
        
        # Focus on first input
        self.root.after(100, lambda: self.date_entry.focus())
        
    def create_header(self):
        """Create application header"""
        header_frame = ctk.CTkFrame(self.root, height=80, fg_color=self.colors['primary'])
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo and title
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        logo_label = ctk.CTkLabel(
            title_frame,
            text="📊",
            font=ctk.CTkFont(size=24),
            text_color=self.colors['accent']
        )
        logo_label.grid(row=0, column=0, padx=(0, 10))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Accounting Journal Pro",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.grid(row=0, column=1)
        
        # Header buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, sticky="e", padx=20, pady=10)
        
        self.export_btn = ctk.CTkButton(
            button_frame,
            text="📄 Export CSV",
            command=self.export_csv,
            width=120,
            height=35,
            fg_color=self.colors['success'],
            hover_color="#218838"
        )
        self.export_btn.grid(row=0, column=0, padx=5)
        
        self.clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear All",
            command=self.clear_all_entries,
            width=120,
            height=35,
            fg_color=self.colors['danger'],
            hover_color="#c82333"
        )
        self.clear_btn.grid(row=0, column=1, padx=5)
        
    def create_main_content(self):
        """Create main content area with entry form and entries list"""
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Entry form (left side)
        self.create_entry_form(main_frame)
        
        # Entries list (right side)
        self.create_entries_list(main_frame)
        
    def create_entry_form(self, parent):
        """Create journal entry form"""
        form_frame = ctk.CTkFrame(parent)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Form title
        title_label = ctk.CTkLabel(
            form_frame,
            text="📝 New Journal Entry",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['primary']
        )
        title_label.grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # Date and Narration section
        date_narr_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_narr_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        date_narr_frame.grid_columnconfigure(1, weight=1)
        
        # Date
        date_label = ctk.CTkLabel(date_narr_frame, text="📅 Date:", font=ctk.CTkFont(weight="bold"))
        date_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.date_entry = ctk.CTkEntry(
            date_narr_frame,
            width=150,
            placeholder_text="YYYY-MM-DD"
        )
        self.date_entry.grid(row=1, column=0, sticky="w", padx=(0, 20))
        # Set today's date
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Narration
        narr_label = ctk.CTkLabel(date_narr_frame, text="💬 Narration:", font=ctk.CTkFont(weight="bold"))
        narr_label.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.narration_entry = ctk.CTkEntry(
            date_narr_frame,
            placeholder_text="Enter transaction description...",
            fg_color=self.colors['narration'],
            border_color=self.colors['warning']
        )
        self.narration_entry.grid(row=1, column=1, sticky="ew")
        
        # Accounts section
        accounts_label = ctk.CTkLabel(
            form_frame,
            text="📋 Account Entries",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['primary']
        )
        accounts_label.grid(row=2, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # Accounts container with scrollbar
        self.accounts_frame = ctk.CTkScrollableFrame(form_frame, height=200)
        self.accounts_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=5)
        self.accounts_frame.grid_columnconfigure(0, weight=1)
        
        # Add account button
        add_account_btn = ctk.CTkButton(
            form_frame,
            text="➕ Add Account",
            command=self.add_account_row,
            width=150,
            fg_color=self.colors['secondary'],
            hover_color="#1e3c72"
        )
        add_account_btn.grid(row=4, column=0, pady=10, sticky="w", padx=20)
        
        # Running totals
        self.create_running_totals(form_frame)
        
        # Submit buttons
        self.create_submit_buttons(form_frame)
        
        # Add initial account rows
        self.add_account_row()
        self.add_account_row()
        
    def create_running_totals(self, parent):
        """Create running totals display"""
        totals_frame = ctk.CTkFrame(parent, height=100)
        totals_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=15)
        totals_frame.grid_propagate(False)
        totals_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Totals title
        totals_title = ctk.CTkLabel(
            totals_frame,
            text="🧮 Running Totals",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        totals_title.grid(row=0, column=0, columnspan=3, pady=(10, 5))
        
        # Debit total
        debit_frame = ctk.CTkFrame(totals_frame, fg_color=self.colors['success'])
        debit_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(debit_frame, text="Total Debit", font=ctk.CTkFont(weight="bold"), text_color="white").pack(pady=2)
        self.debit_total_label = ctk.CTkLabel(debit_frame, text="₹0.00", font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        self.debit_total_label.pack(pady=2)
        
        # Credit total
        credit_frame = ctk.CTkFrame(totals_frame, fg_color=self.colors['danger'])
        credit_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(credit_frame, text="Total Credit", font=ctk.CTkFont(weight="bold"), text_color="white").pack(pady=2)
        self.credit_total_label = ctk.CTkLabel(credit_frame, text="₹0.00", font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        self.credit_total_label.pack(pady=2)
        
        # Difference
        diff_frame = ctk.CTkFrame(totals_frame, fg_color=self.colors['warning'])
        diff_frame.grid(row=1, column=2, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(diff_frame, text="Difference", font=ctk.CTkFont(weight="bold"), text_color="white").pack(pady=2)
        self.diff_total_label = ctk.CTkLabel(diff_frame, text="₹0.00", font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        self.diff_total_label.pack(pady=2)
        
    def create_submit_buttons(self, parent):
        """Create submit and clear buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=6, column=0, pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Entry",
            command=self.save_entry,
            width=200,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors['success'],
            hover_color="#218838"
        )
        save_btn.grid(row=0, column=0, padx=10)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Clear Form",
            command=self.clear_form,
            width=200,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors['warning'],
            hover_color="#e0a800"
        )
        clear_btn.grid(row=0, column=1, padx=10)
        
    def add_account_row(self):
        """Add a new account entry row"""
        row_frame = ctk.CTkFrame(self.accounts_frame)
        row_frame.grid(sticky="ew", pady=5)
        row_frame.grid_columnconfigure(0, weight=2)
        row_frame.grid_columnconfigure(1, weight=1)
        row_frame.grid_columnconfigure(2, weight=1)
        
        # Account name with autocomplete
        name_entry = ctk.CTkEntry(
            row_frame,
            placeholder_text="Account name..."
        )
        name_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=10)
        
        # Type selection
        type_var = ctk.StringVar(value="Select Type")
        type_combo = ctk.CTkComboBox(
            row_frame,
            values=["Debit", "Credit"],
            variable=type_var,
            command=lambda choice: self.update_totals()
        )
        type_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        # Amount
        amount_entry = ctk.CTkEntry(
            row_frame,
            placeholder_text="Amount..."
        )
        amount_entry.grid(row=0, column=2, sticky="ew", padx=5, pady=10)
        
        # Remove button
        remove_btn = ctk.CTkButton(
            row_frame,
            text="❌",
            width=30,
            command=lambda: self.remove_account_row(row_frame),
            fg_color=self.colors['danger'],
            hover_color="#c82333"
        )
        remove_btn.grid(row=0, column=3, padx=5, pady=10)
        
        # Bind events for real-time calculation
        amount_entry.bind('<KeyRelease>', lambda e: self.update_totals())
        
        # Store references
        setattr(row_frame, 'name_entry', name_entry)
        setattr(row_frame, 'type_combo', type_combo)
        setattr(row_frame, 'amount_entry', amount_entry)
        
        # Add autocomplete for account names
        self.setup_autocomplete(name_entry)
        
        # Focus on new entry
        name_entry.focus()
        
        self.update_totals()
        
    def setup_autocomplete(self, entry):
        """Setup autocomplete for account names"""
        def on_keyrelease(event):
            current_text = entry.get().lower()
            if len(current_text) > 1:
                matches = [acc for acc in self.common_accounts if acc.lower().startswith(current_text)]
                if matches and matches[0].lower() != current_text:
                    # Simple autocomplete - replace with first match
                    # entry.delete(0, tk.END)
                    # entry.insert(0, matches[0])
                    # entry.select_range(len(current_text), tk.END)
                    pass
        
        entry.bind('<KeyRelease>', on_keyrelease)
        
    def remove_account_row(self, row_frame):
        """Remove an account row"""
        # Ensure at least one row remains
        if len(self.accounts_frame.winfo_children()) > 1:
            row_frame.destroy()
            self.update_totals()
        else:
            messagebox.showwarning("Warning", "At least one account entry is required!")
            
    def update_totals(self):
        """Update running totals display"""
        total_debit = 0
        total_credit = 0
        
        for child in self.accounts_frame.winfo_children():
            if hasattr(child, 'amount_entry') and hasattr(child, 'type_combo'):
                try:
                    amount = float(getattr(child, 'amount_entry').get() or 0)
                    acc_type = getattr(child, 'type_combo').get()
                    
                    if acc_type == "Debit":
                        total_debit += amount
                    elif acc_type == "Credit":
                        total_credit += amount
                except ValueError:
                    continue
        
        difference = abs(total_debit - total_credit)
        
        # Update display
        self.debit_total_label.configure(text=f"₹{total_debit:.2f}")
        self.credit_total_label.configure(text=f"₹{total_credit:.2f}")
        self.diff_total_label.configure(text=f"₹{difference:.2f}")
        
        # Change difference color based on balance
        if difference < 0.01:
            try:
                self.diff_total_label.master.configure(fg_color=self.colors['success'])
            except:
                pass
        else:
            try:
                self.diff_total_label.master.configure(fg_color=self.colors['warning'])
            except:
                pass
            
    def save_entry(self):
        """Save the current journal entry"""
        # Validate form
        if not self.validate_entry():
            return
            
        # Collect account data
        accounts = []
        for child in self.accounts_frame.winfo_children():
            if hasattr(child, 'name_entry') and hasattr(child, 'type_combo') and hasattr(child, 'amount_entry'):
                name = getattr(child, 'name_entry').get().strip()
                acc_type = getattr(child, 'type_combo').get()
                try:
                    amount = float(getattr(child, 'amount_entry').get() or 0)
                    if name and acc_type in ["Debit", "Credit"] and amount > 0:
                        accounts.append({
                            'name': name,
                            'type': acc_type.lower(),
                            'amount': amount
                        })
                except ValueError:
                    continue
        
        # Create entry
        entry = {
            'id': self.entry_counter,
            'date': self.date_entry.get(),
            'narration': self.narration_entry.get(),
            'accounts': accounts,
            'timestamp': datetime.now().isoformat()
        }
        
        self.entries.append(entry)
        self.entry_counter += 1
        
        # Update entries list
        self.refresh_entries_list()
        
        # Clear form
        self.clear_form()
        
        # Show success message
        self.show_notification("Entry saved successfully!", "success")
        
        # Focus on date field for next entry
        self.date_entry.focus()
        
    def validate_entry(self):
        """Validate journal entry before saving"""
        # Check date
        if not self.date_entry.get().strip():
            messagebox.showerror("Validation Error", "Date is required!")
            self.date_entry.focus()
            return False
            
        # Check narration
        if not self.narration_entry.get().strip():
            messagebox.showerror("Validation Error", "Narration is required!")
            self.narration_entry.focus()
            return False
            
        # Check accounts
        valid_accounts = 0
        total_debit = 0
        total_credit = 0
        
        for child in self.accounts_frame.winfo_children():
            if hasattr(child, 'name_entry') and hasattr(child, 'type_combo') and hasattr(child, 'amount_entry'):
                name = getattr(child, 'name_entry').get().strip()
                acc_type = getattr(child, 'type_combo').get()
                try:
                    amount = float(getattr(child, 'amount_entry').get() or 0)
                    if name and acc_type in ["Debit", "Credit"] and amount > 0:
                        valid_accounts += 1
                        if acc_type == "Debit":
                            total_debit += amount
                        else:
                            total_credit += amount
                except ValueError:
                    continue
        
        if valid_accounts == 0:
            messagebox.showerror("Validation Error", "At least one valid account entry is required!")
            return False
            
        # Check if entry is balanced
        if abs(total_debit - total_credit) > 0.01:
            result = messagebox.askyesno(
                "Entry Not Balanced",
                f"Entry is not balanced!\n"
                f"Total Debit: ₹{total_debit:.2f}\n"
                f"Total Credit: ₹{total_credit:.2f}\n"
                f"Difference: ₹{abs(total_debit - total_credit):.2f}\n\n"
                f"Do you want to save anyway?"
            )
            if not result:
                return False
                
        return True
        
    def clear_form(self):
        """Clear the entry form"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.narration_entry.delete(0, tk.END)
        
        # Clear all account rows except first two
        children = list(self.accounts_frame.winfo_children())
        for child in children[2:]:
            child.destroy()
            
        # Clear remaining rows
        for child in children[:2]:
            if hasattr(child, 'name_entry'):
                getattr(child, 'name_entry').delete(0, tk.END)
                getattr(child, 'type_combo').set("Select Type")
                getattr(child, 'amount_entry').delete(0, tk.END)
                
        self.update_totals()
        self.date_entry.focus()
        
    def create_entries_list(self, parent):
        """Create entries list display"""
        list_frame = ctk.CTkFrame(parent)
        list_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        list_frame.grid_rowconfigure(1, weight=1)
        
        # List title
        title_label = ctk.CTkLabel(
            list_frame,
            text="📋 Recent Entries",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['primary']
        )
        title_label.grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # Entries display with scrollbar
        self.entries_display = ctk.CTkScrollableFrame(list_frame)
        self.entries_display.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Session totals
        self.create_session_totals(list_frame)
        
    def create_session_totals(self, parent):
        """Create session totals display"""
        totals_frame = ctk.CTkFrame(parent)
        totals_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            totals_frame,
            text="📊 Session Totals",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(15, 10))
        
        self.session_debit_label = ctk.CTkLabel(
            totals_frame,
            text="Total Debit: ₹0.00",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['debit']
        )
        self.session_debit_label.pack(pady=2)
        
        self.session_credit_label = ctk.CTkLabel(
            totals_frame,
            text="Total Credit: ₹0.00",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['credit']
        )
        self.session_credit_label.pack(pady=2)
        
        self.session_balance_label = ctk.CTkLabel(
            totals_frame,
            text="Balance: ₹0.00",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.session_balance_label.pack(pady=(5, 15))
        
    def refresh_entries_list(self):
        """Refresh the entries list display"""
        # Clear existing entries
        for widget in self.entries_display.winfo_children():
            widget.destroy()
            
        # Display entries in reverse order (newest first)
        for entry in reversed(self.entries):
            self.create_entry_widget(entry)
            
        # Update session totals
        self.update_session_totals()
        
    def create_entry_widget(self, entry):
        """Create widget for displaying a single entry"""
        entry_frame = ctk.CTkFrame(self.entries_display)
        entry_frame.pack(fill="x", pady=5)
        
        # Entry header
        header_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        date_label = ctk.CTkLabel(
            header_frame,
            text=f"📅 {entry['date']}",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        date_label.pack(side="left")
        
        delete_btn = ctk.CTkButton(
            header_frame,
            text="🗑️",
            width=30,
            height=25,
            command=lambda: self.delete_entry(entry['id']),
            fg_color=self.colors['danger'],
            hover_color="#c82333"
        )
        delete_btn.pack(side="right")
        
        # Narration
        narr_label = ctk.CTkLabel(
            entry_frame,
            text=entry['narration'],
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['narration'],
            corner_radius=5
        )
        narr_label.pack(fill="x", padx=15, pady=5)
        
        # Accounts
        for account in entry['accounts']:
            acc_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
            acc_frame.pack(fill="x", padx=15, pady=2)
            
            acc_text = f"{account['name']}"
            amount_text = f"{'Dr.' if account['type'] == 'debit' else 'Cr.'} ₹{account['amount']:.2f}"
            
            acc_label = ctk.CTkLabel(acc_frame, text=acc_text, font=ctk.CTkFont(size=11))
            acc_label.pack(side="left")
            
            amount_label = ctk.CTkLabel(
                acc_frame,
                text=amount_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colors['debit'] if account['type'] == 'debit' else self.colors['credit']
            )
            amount_label.pack(side="right")
            
        # Add spacing
        spacer = ctk.CTkLabel(entry_frame, text="", height=5)
        spacer.pack()
        
    def delete_entry(self, entry_id):
        """Delete an entry"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?"):
            self.entries = [entry for entry in self.entries if entry['id'] != entry_id]
            self.refresh_entries_list()
            self.show_notification("Entry deleted successfully!", "info")
            
    def update_session_totals(self):
        """Update session totals display"""
        total_debit = 0
        total_credit = 0
        
        for entry in self.entries:
            for account in entry['accounts']:
                if account['type'] == 'debit':
                    total_debit += account['amount']
                else:
                    total_credit += account['amount']
                    
        balance = total_debit - total_credit
        
        self.session_debit_label.configure(text=f"Total Debit: ₹{total_debit:.2f}")
        self.session_credit_label.configure(text=f"Total Credit: ₹{total_credit:.2f}")
        self.session_balance_label.configure(text=f"Balance: ₹{balance:.2f}")
        
    def export_csv(self):
        """Export entries to CSV file"""
        if not self.entries:
            messagebox.showwarning("No Data", "No entries to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save Journal Entries",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"journal_entries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
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
                
                self.show_notification(f"Entries exported successfully to {filename}", "success")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export entries:\n{str(e)}")
                
    def clear_all_entries(self):
        """Clear all entries"""
        if self.entries and messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all entries?"):
            self.entries.clear()
            self.entry_counter = 1
            self.refresh_entries_list()
            self.show_notification("All entries cleared!", "info")
            
    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = ctk.CTkFrame(self.root, height=30, fg_color=self.colors['light'])
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self.status_frame.grid_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready - Use keyboard shortcuts: Enter (next field), Ctrl+N (new account), Ctrl+S (save)",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['dark']
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
    def setup_keyboard_navigation(self):
        """Setup keyboard navigation and shortcuts"""
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.add_account_row())
        self.root.bind('<Control-s>', lambda e: self.save_entry())
        self.root.bind('<Control-e>', lambda e: self.export_csv())
        self.root.bind('<F1>', lambda e: self.show_help())
        
        # Focus navigation with Enter key
        def on_enter(event):
            widget = event.widget
            # Get all focusable widgets
            focusable = []
            
            def collect_focusable(parent):
                for child in parent.winfo_children():
                    if isinstance(child, (ctk.CTkEntry, ctk.CTkComboBox, ctk.CTkButton)):
                        focusable.append(child)
                    collect_focusable(child)
                    
            collect_focusable(self.root)
            
            try:
                current_index = focusable.index(widget)
                next_index = (current_index + 1) % len(focusable)
                focusable[next_index].focus()
            except (ValueError, IndexError):
                pass
                
        # Bind Enter key to all entries
        def bind_enter_recursively(parent):
            for child in parent.winfo_children():
                if isinstance(child, ctk.CTkEntry):
                    child.bind('<Return>', on_enter)
                bind_enter_recursively(child)
                
        self.root.after(500, lambda: bind_enter_recursively(self.root))
        
    def show_help(self):
        """Show help dialog"""
        help_text = """
Accounting Journal Pro - Help

Keyboard Shortcuts:
• Enter: Move to next field
• Ctrl+N: Add new account row
• Ctrl+S: Save current entry
• Ctrl+E: Export to CSV
• F1: Show this help

Features:
• Double-entry bookkeeping validation
• Real-time total calculation
• CSV export functionality
• Professional interface inspired by Tally ERP

Tips:
• Ensure debits equal credits before saving
• Use meaningful narrations for better tracking
• Export regularly to backup your data
        """
        
        messagebox.showinfo("Help", help_text)
        
    def show_notification(self, message, msg_type="info"):
        """Show notification message"""
        if msg_type == "success":
            messagebox.showinfo("Success", message)
        elif msg_type == "error":
            messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Info", message)
            
    def run(self):
        """Start the application"""
        # Hide main window initially
        self.root.withdraw()
        
        # Start the main loop
        self.root.mainloop()

def main():
    """Main function to run the application"""
    try:
        app = ModernAccountingJournal()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}")

if __name__ == "__main__":
    main()