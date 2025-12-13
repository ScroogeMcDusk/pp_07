# Device Inspection App (Python, Tkinter, MS SQL Server)

This project is an educational/demo Python application matching the user's specification.

Features:
- Connect to MS SQL Server via pyodbc (enter server, database, driver, login, password)
- Generate and preview connection string
- Test connection using pyodbc
- CRUD (Create, Read, Update, Delete) for tables:
  - Devices (Устройства)
  - Inspections (Проверка)
  - Defects (Дефекты)
  - Users (Пользователи)
- Administer SQL Server logins/users and roles via T-SQL commands
- Dialogs for adding/editing records
- Basic UI inspired by provided images (Tkinter)

Requirements:
- Python 3.8+
- pyodbc
- tkinter (usually included with Python)

Install requirements:
```
pip install -r requirements.txt
```

How to run:
```
python main.py
```

Notes:
- This app executes T-SQL statements against the SQL Server you connect to. Use with care and preferably a test database.
- The code contains placeholders and guidance where you may need to adapt for your environment (ODBC driver names, permissions, etc.).
