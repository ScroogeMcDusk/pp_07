# dialogs.py - Tkinter dialog windows for add/edit and connection input
import tkinter as tk
from tkinter import simpledialog, messagebox

class ConnectionDialog(simpledialog.Dialog):
    def body(self, master):
        self.title('Connection settings')
        tk.Label(master, text='Сервер:').grid(row=0, sticky='e')
        tk.Label(master, text='База данных:').grid(row=1, sticky='e')
        tk.Label(master, text='Драйвер:').grid(row=2, sticky='e')
        tk.Label(master, text='Используйте доверенное соединение:').grid(row=3, sticky='e')
        tk.Label(master, text='Пользователь:').grid(row=4, sticky='e')
        tk.Label(master, text='Пароль:').grid(row=5, sticky='e')

        self.e_server = tk.Entry(master); self.e_server.grid(row=0, column=1)
        self.e_db = tk.Entry(master); self.e_db.grid(row=1, column=1)
        self.e_driver = tk.Entry(master); self.e_driver.insert(0, 'ODBC Driver 17 for SQL Server'); self.e_driver.grid(row=2, column=1)
        self.var_trusted = tk.IntVar(); self.c_trusted = tk.Checkbutton(master, variable=self.var_trusted); self.c_trusted.grid(row=3, column=1, sticky='w')
        self.e_user = tk.Entry(master); self.e_user.grid(row=4, column=1)
        self.e_pwd = tk.Entry(master, show='*'); self.e_pwd.grid(row=5, column=1)
        return self.e_server

    def apply(self):
        self.result = {
            'server': self.e_server.get(),
            'database': self.e_db.get(),
            'driver': self.e_driver.get(),
            'trusted': bool(self.var_trusted.get()),
            'user': self.e_user.get(),
            'password': self.e_pwd.get()
        }

class RecordDialog(simpledialog.Dialog):
    def __init__(self, master, title, fields, values=None):
        self.fields = fields
        self.values = values or {}
        super().__init__(master, title=title)

    def body(self, master):
        self.entries = {}
        for i,f in enumerate(self.fields):
            tk.Label(master, text=f + ':').grid(row=i, column=0, sticky='e')
            e = tk.Entry(master)
            e.grid(row=i, column=1)
            if f in self.values:
                e.insert(0, str(self.values[f]))
            self.entries[f] = e
        return list(self.entries.values())[0]

    def apply(self):
        self.result = {k: e.get() for k,e in self.entries.items()}
