## Bookstore Application

A bookstore desktop application for customers and managers; Final Project for TAMU CSCE 310

This repository contains a desktop-based bookstore system with isolated customer and manager functionality. The application consists of a FreeSimpleGUI frontend, a Flask REST API backend, and a MySQL database connected via SQLAlchemy. Core features include book catalog browsing, renting and buying books, order management, HTML bill generation, and sandboxed email sending through a Mailtrap.io SMTP configuration. 

## Features

- Customer and manager roles with JWT-based authentication and role-based authorization.   
- Desktop GUI for browsing books, placing orders, and managing catalog and orders (for managers).   
- REST API with routes for users, books, authors, orders, and keyword-based search/filtering.   
- MySQL database with normalized schema, many-to-many book–keyword mapping, and indexed lookup fields.   
- Simple HTML bill generation and email sending via Mailtrap.io SMTP sandbox.   

## Environment Setup (.env)

Create a `.env` file in the project root with values matching your local setup. At minimum, the following variables are expected by the config classes and database helpers: 

```ini
# Database
DB_HOST=localhost
DB_PORT=your_db_port
DB_NAME=bookstore
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# JWT
JWT_SECRET=your_jwt_secret_key

# Mailtrap SMTP (sandbox)
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your_mailtrap_username
SMTP_PASSWORD=your_mailtrap_password
SMTP_FROM_EMAIL=bookstore@example.com
```

The exact variable names should match what is loaded in your configuration modules. If any name differs in your code, those should be updated here rather than introducing new ones. 

## Database Migrations and Seeding

1. Create the target database in MySQL (for example, `bookstore`).  
2. From the project root, run the migration script to apply the numbered SQL files:  

   ```bash
   python -m migrations.run_migrations
   ```  

3. Seed the database with sample data using SQLAlchemy and Faker:  

   ```bash
   python -m migrations.seed
   ```  

These steps create all tables, indexes, and initial sample data, including books, authors, users, and keywords. 

## Running the API

From the project root, start the Flask API:

```bash
python -m api.app
```

This runs a local REST API that exposes the users, books, authors, and orders routes and connects to the MySQL database via SQLAlchemy. Ensure the `.env` file is accessible so configuration values can be loaded. 

## Running the GUI

In a separate terminal, start the FreeSimpleGUI desktop client:

```bash
python -m frontend.main
```

The GUI connects to the locally running API, manages session state and JWTs, and provides separate flows for customers and managers. 
