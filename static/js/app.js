// Global variables
let accountCounter = 0;
const commonAccounts = [
    'Cash', 'Bank', 'Capital', 'Sales', 'Purchases', 'Rent', 'Salary', 
    'Electricity', 'Office Expenses', 'Furniture', 'Building', 'Land',
    'Debtors', 'Creditors', 'Stock', 'Interest', 'Commission', 'Discount'
];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Show loading screen and fade in main app
    setTimeout(() => {
        document.getElementById('loadingScreen').style.display = 'none';
        document.getElementById('mainApp').classList.add('fade-in');
    }, 2000);

    // Initialize form
    initializeForm();
    
    // Add event listeners
    addEventListeners();
    
    // Add initial account rows
    addAccountRow();
    addAccountRow();
});

// Initialize form functionality
function initializeForm() {
    // Set up keyboard navigation
    setupKeyboardNavigation();
    
    // Focus on first input
    setTimeout(() => {
        const firstInput = document.getElementById('entry_date');
        if (firstInput) firstInput.focus();
    }, 2100);
}

// Add event listeners
function addEventListeners() {
    // Add account button
    document.getElementById('addAccountBtn').addEventListener('click', addAccountRow);
    
    // Clear form button
    document.getElementById('clearFormBtn').addEventListener('click', clearForm);
    
    // Form submission
    document.getElementById('entryForm').addEventListener('submit', validateForm);
    
    // Auto-calculate totals on input change
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('amount-input') || 
            e.target.classList.contains('account-type-select')) {
            calculateTotals();
        }
    });
}

// Add a new account row
function addAccountRow() {
    accountCounter++;
    
    const container = document.getElementById('accountsContainer');
    const accountRow = document.createElement('div');
    accountRow.className = 'account-row';
    accountRow.dataset.accountId = accountCounter;
    
    accountRow.innerHTML = `
        <div class="row align-items-center">
            <div class="col-md-4 mb-2">
                <label class="form-label">Account Name</label>
                <input type="text" class="form-control account-name-input" 
                       name="account_name" 
                       placeholder="Enter account name..."
                       list="accountSuggestions${accountCounter}" required>
                <datalist id="accountSuggestions${accountCounter}">
                    ${commonAccounts.map(account => `<option value="${account}">`).join('')}
                </datalist>
            </div>
            <div class="col-md-3 mb-2">
                <label class="form-label">Type</label>
                <select class="form-select account-type-select" name="account_type" required>
                    <option value="">Select...</option>
                    <option value="debit">Debit</option>
                    <option value="credit">Credit</option>
                </select>
            </div>
            <div class="col-md-3 mb-2">
                <label class="form-label">Amount (₹)</label>
                <input type="number" class="form-control amount-input" 
                       name="account_amount" 
                       placeholder="0.00" 
                       step="0.01" min="0" required>
            </div>
            <div class="col-md-2 mb-2 d-flex align-items-end">
                <button type="button" class="btn btn-outline-danger btn-sm remove-account-btn" 
                        onclick="removeAccountRow(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    container.appendChild(accountRow);
    
    // Add visual effect
    accountRow.style.opacity = '0';
    accountRow.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        accountRow.style.transition = 'all 0.3s ease';
        accountRow.style.opacity = '1';
        accountRow.style.transform = 'translateY(0)';
    }, 10);
    
    // Update account row styling based on type
    const typeSelect = accountRow.querySelector('.account-type-select');
    typeSelect.addEventListener('change', function() {
        updateAccountRowStyling(accountRow, this.value);
    });
    
    // Focus on the new account name input
    const nameInput = accountRow.querySelector('.account-name-input');
    nameInput.focus();
    
    // Calculate totals
    calculateTotals();
}

// Remove account row
function removeAccountRow(button) {
    const accountRow = button.closest('.account-row');
    const container = document.getElementById('accountsContainer');
    
    if (container.children.length > 1) {
        accountRow.style.transition = 'all 0.3s ease';
        accountRow.style.opacity = '0';
        accountRow.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            accountRow.remove();
            calculateTotals();
        }, 300);
    } else {
        alert('At least one account entry is required!');
    }
}

// Update account row styling based on type
function updateAccountRowStyling(row, type) {
    row.classList.remove('debit', 'credit');
    if (type) {
        row.classList.add(type);
    }
}

// Calculate running totals
function calculateTotals() {
    let totalDebit = 0;
    let totalCredit = 0;
    
    const accountRows = document.querySelectorAll('.account-row');
    
    accountRows.forEach(row => {
        const typeSelect = row.querySelector('.account-type-select');
        const amountInput = row.querySelector('.amount-input');
        
        const type = typeSelect.value;
        const amount = parseFloat(amountInput.value) || 0;
        
        if (type === 'debit') {
            totalDebit += amount;
        } else if (type === 'credit') {
            totalCredit += amount;
        }
    });
    
    // Update display
    document.getElementById('totalDebit').textContent = totalDebit.toFixed(2);
    document.getElementById('totalCredit').textContent = totalCredit.toFixed(2);
    
    const difference = Math.abs(totalDebit - totalCredit);
    document.getElementById('totalDifference').textContent = difference.toFixed(2);
    
    // Update difference color
    const differenceElement = document.getElementById('totalDifference');
    const balanceBox = differenceElement.closest('.balance-total');
    
    if (difference < 0.01) {
        balanceBox.style.borderColor = '#28a745';
        differenceElement.style.color = '#28a745';
    } else {
        balanceBox.style.borderColor = '#ffc107';
        differenceElement.style.color = '#ffc107';
    }
}

// Setup keyboard navigation
function setupKeyboardNavigation() {
    const form = document.getElementById('entryForm');
    
    form.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            
            const currentElement = document.activeElement;
            const formElements = form.querySelectorAll(
                'input:not([type="submit"]), select, textarea, button[type="submit"]'
            );
            
            const currentIndex = Array.from(formElements).indexOf(currentElement);
            
            if (currentIndex >= 0 && currentIndex < formElements.length - 1) {
                formElements[currentIndex + 1].focus();
            } else if (currentIndex === formElements.length - 1) {
                // Last element - submit form
                form.submit();
            }
        }
        
        // Ctrl + N for new account row
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            addAccountRow();
        }
        
        // Ctrl + S for save
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            form.submit();
        }
    });
}

// Clear form
function clearForm() {
    if (confirm('Are you sure you want to clear all form data?')) {
        document.getElementById('entryForm').reset();
        
        // Clear all account rows except first two
        const container = document.getElementById('accountsContainer');
        while (container.children.length > 2) {
            container.removeChild(container.lastChild);
        }
        
        // Reset account counter
        accountCounter = 2;
        
        // Reset totals
        calculateTotals();
        
        // Focus on date field
        document.getElementById('entry_date').focus();
        
        // Show success message
        showNotification('Form cleared successfully!', 'info');
    }
}

// Validate form before submission
function validateForm(e) {
    const totalDebit = parseFloat(document.getElementById('totalDebit').textContent);
    const totalCredit = parseFloat(document.getElementById('totalCredit').textContent);
    const difference = Math.abs(totalDebit - totalCredit);
    
    if (difference > 0.01) {
        e.preventDefault();
        alert(`Entry is not balanced!\nTotal Debit: ₹${totalDebit.toFixed(2)}\nTotal Credit: ₹${totalCredit.toFixed(2)}\nDifference: ₹${difference.toFixed(2)}\n\nPlease balance your entry before saving.`);
        return false;
    }
    
    // Check if at least one account has values
    const accountRows = document.querySelectorAll('.account-row');
    let hasValidAccount = false;
    
    accountRows.forEach(row => {
        const nameInput = row.querySelector('.account-name-input');
        const typeSelect = row.querySelector('.account-type-select');
        const amountInput = row.querySelector('.amount-input');
        
        if (nameInput.value.trim() && typeSelect.value && parseFloat(amountInput.value) > 0) {
            hasValidAccount = true;
        }
    });
    
    if (!hasValidAccount) {
        e.preventDefault();
        alert('Please add at least one valid account entry!');
        return false;
    }
    
    // Show loading state
    const submitBtn = document.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
    submitBtn.disabled = true;
    
    // Reset button after delay (in case of validation errors)
    setTimeout(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }, 5000);
    
    return true;
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
    `;
    
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Add smooth scrolling for navigation
function smoothScrollTo(element) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
}

// Export function for external use
window.AccountingJournal = {
    addAccountRow,
    removeAccountRow,
    calculateTotals,
    clearForm,
    showNotification
};

// Console welcome message
console.log(`
🔢 Accounting Journal Pro
Professional Journal Entry System
Built with Flask & Modern Web Technologies

Keyboard Shortcuts:
• Enter: Navigate to next field
• Ctrl+N: Add new account row
• Ctrl+S: Save entry
• Tab: Standard navigation

© 2024 Accounting Journal Pro
`);
