# Accounting Journal Pro

## Overview

Accounting Journal Pro is a professional web-based double-entry bookkeeping system built with Flask. The application allows users to create, manage, and export accounting journal entries with automatic calculation of debit and credit totals. It features a modern, responsive interface with Bootstrap styling and provides essential accounting functionality including journal entry creation, validation, and CSV export capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Bootstrap 5.3.0 for responsive UI components
- **Styling**: Custom CSS with Google Fonts (Inter) and Font Awesome icons
- **JavaScript**: Vanilla JavaScript for form validation, dynamic account row management, and keyboard navigation
- **Design Pattern**: Single-page application with server-side rendering
- **User Experience**: Professional loading screen with fade-in animations and intuitive form controls

### Backend Architecture
- **Framework**: Flask (Python) with session-based state management
- **Architecture Pattern**: MVC (Model-View-Controller) structure
- **Data Storage**: Server-side sessions for temporary data persistence
- **Routing**: RESTful route handlers for CRUD operations
- **Business Logic**: Double-entry accounting validation with automatic debit/credit balancing

### Data Management
- **Storage Strategy**: Session-based temporary storage (no persistent database)
- **Data Structure**: JSON-like objects stored in Flask sessions
- **Export Capability**: CSV generation using Python's built-in csv module
- **Session Management**: Automatic initialization and counter tracking for entries

### Key Features
- **Double-Entry Validation**: Ensures debits equal credits before submission
- **Dynamic Form Management**: JavaScript-powered addition/removal of account rows
- **Professional UI**: Loading screens, animations, and responsive design
- **Export Functionality**: CSV download of all journal entries
- **Session Persistence**: Maintains data across browser sessions until manually cleared

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: UI framework for responsive design and components
- **Font Awesome 6.4.0**: Icon library for professional iconography
- **Google Fonts (Inter)**: Typography for modern, readable interface

### Backend Dependencies
- **Flask**: Core web framework for Python
- **Built-in Python Modules**: 
  - `csv` for export functionality
  - `datetime` for timestamp management
  - `logging` for application monitoring
  - `io.StringIO` for in-memory file operations

### Browser APIs
- **Session Storage**: Client-side temporary data persistence
- **DOM Manipulation**: Dynamic form field management
- **Event Handling**: Keyboard navigation and form validation

### Development Environment
- **Python Runtime**: Server-side application execution
- **Static File Serving**: CSS, JavaScript, and asset delivery through Flask
- **Template Engine**: Jinja2 (Flask's default) for server-side rendering