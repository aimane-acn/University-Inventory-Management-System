# 📦 Système de Gestion des Stocks Universitaire

## Overview
This project is a web application for managing university equipment and tracking resources across departments.  
Users can submit supply requests, manage stock levels, and oversee order workflows through role-based interfaces.

## Architecture
The system consists of three main components:

- **Web Application (Django)**  
  Handles user authentication, role-based access, order management, and inventory tracking.

- **Business Logic Layer (Django Apps)**  
  Manages purchase orders, needs expressions, stock catalog, director approval workflows, and stock deductions.

- **Database (SQLite / Oracle)**  
  Stores users, departments, inventory items, detailed orders, and status archives.

## Tech Stack
- Python  
- Django  
- HTML, CSS, JavaScript  
- Bootstrap  
- SQLite  

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/aimane-acn/Application-Gestion-de-Stock-Universite.git
cd Application-Gestion-de-Stock-Universite
```

### 2. Setup environment and install dependencies
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

## Run the Application

### 1. Apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Start the web server
```bash
python manage.py runserver
```

## Access
Open your browser and go to:  
http://127.0.0.1:8000

### Demo Accounts
| Role | Username | Password |
| :--- | :--- | :--- |
| Fonctionnaire | `fonctionnaire` | `Aimane123@` |
| Stock Manager | `stock_manager` | `Aimane123@` |
| Directeur | `directeur` | `Aimane123@` |

> Demo accounts are in **read-only mode** to preserve showcase data. To test full features, create your own account at `/signup`.

## Project Structure
```bash
core/             # Django project settings, URLs, middleware
inventory/        # Orders, needs, stock levels, filters, views
stockapp/         # User models (Professeur, Magasinier, Directeur, Admin)
homepage/         # Role-specific sidebars and navigation templates
templates/        # Global UI templates (login, signup)
style/            # CSS stylesheets and assets
db.sqlite3        # Pre-configured database with showcase dataset
manage.py         # Django management script
requirements.txt  # Python dependencies
```

## Notes
- Use Python 3.8.10  
- The database `db.sqlite3` is included with pre-loaded demo data  
- Skip migrations if using the included database  
- Django Admin is available at `/aimane/`  

## Author
Aimane Achibane

---

⭐ If you like this project, consider giving it a star on GitHub!
