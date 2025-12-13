# gui.py - main application GUI
import tkinter as tk
from tkinter import ttk, messagebox
from db import DBConnection
from dialogs import ConnectionDialog, RecordDialog
import threading

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Приложение для проверки устройств')
        self.geometry('900x600')
        self.db = DBConnection()
        self.create_menu()
        self.create_toolbar()
        self.current_table = None
        self.tree = None
        self.create_table_view()

    def create_menu(self):
        menubar = tk.Menu(self)
        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label='Подключение...', command=self.connect_dialog)
        filem.add_command(label='Выход', command=self.quit)
        menubar.add_cascade(label='Файл', menu=filem)

        dbm = tk.Menu(menubar, tearoff=0)
        dbm.add_command(label='Admin: Создание логина', command=self.admin_create_login)
        dbm.add_command(label='Admin: Создание пользователя', command=self.admin_create_db_user)
        dbm.add_command(label='Admin: Добавление пользователя к роли', command=self.admin_add_user_role)
        menubar.add_cascade(label='Admin', menu=dbm)

        menutables = tk.Menu(menubar, tearoff=0)
        menutables.add_command(label='Девайсы', command=lambda: self.load_table('Девайсы'))
        menutables.add_command(label='Проверка', command=lambda: self.load_table('Проверка'))
        menutables.add_command(label='Дефекты', command=lambda: self.load_table('Дефекты'))
        menutables.add_command(label='Пользователи', command=lambda: self.load_table('Пользователи'))
        menubar.add_cascade(label='Таблицы', menu=menutables)

        self.config(menu=menubar)

    def create_toolbar(self):
        frame = tk.Frame(self)
        frame.pack(side='top', fill='x')
        btn_add = tk.Button(frame, text='Добавить', command=self.add_record); btn_add.pack(side='left')
        btn_edit = tk.Button(frame, text='Изменить', command=self.edit_record); btn_edit.pack(side='left')
        btn_del = tk.Button(frame, text='Удалить', command=self.delete_record); btn_del.pack(side='left')
        btn_refresh = tk.Button(frame, text='Обновить', command=self.refresh); btn_refresh.pack(side='left')

    def create_table_view(self):
        frm = tk.Frame(self)
        frm.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(frm)
        self.tree.pack(fill='both', expand=True)

    def connect_dialog(self):
        dlg = ConnectionDialog(self)
        if dlg.result:
            r = dlg.result
            conn_str = self.db.build_conn_str(r['server'], r['database'], r['driver'], uid=r['user'], pwd=r['password'], trusted=r['trusted'])
            ok, msg = self.db.test_connection()
            if ok:
                messagebox.showinfo('OK', msg)
                try:
                    self.db.connect()
                except Exception as e:
                    messagebox.showerror('Error', 'Failed to connect: ' + str(e))
            else:
                messagebox.showerror('Ошибка подключения', msg)

    def load_table(self, table):
        self.current_table = table
        self.title('Device Inspection App - ' + table)
        try:
            cols, rows = self.db.fetch_all(table)
        except Exception as e:
            messagebox.showerror('Error', 'Failed to load table: ' + str(e))
            return
        # clear tree
        for c in self.tree.get_children():
            self.tree.delete(c)
        self.tree['columns'] = cols
        self.tree['show'] = 'headings'
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        for r in rows:
            self.tree.insert('', 'end', values=r)

    def add_record(self):
        if not self.current_table:
            messagebox.showwarning('No table', 'Select a table first')
            return
        # Very generic approach: ask for columns
        cols, rows = self.db.fetch_all(self.current_table)
        # build fields excluding identity columns by heuristic (columns ending with ID and rows have int)
        fields = [c for c in cols if not c.lower().endswith('id')]
        dlg = RecordDialog(self, 'Add record to ' + self.current_table, fields)
        if dlg.result:
            cols_sql = ','.join(f'[{f}]' for f in dlg.result.keys())
            params = tuple(dlg.result.values())
            qmarks = ','.join('?' for _ in params)
            sql = f"INSERT INTO {self.current_table} ({cols_sql}) VALUES ({qmarks})"
            try:
                self.db.execute(sql, params)
                self.refresh()
            except Exception as e:
                messagebox.showerror('Error', str(e))

    def edit_record(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning('Select', 'Select a row first')
            return
        vals = self.tree.item(sel)['values']
        cols = self.tree['columns']
        data = dict(zip(cols, vals))
        # Ask user to edit non-ID fields
        fields = [c for c in cols if not c.lower().endswith('id')]
        dlg = RecordDialog(self, 'Edit record in ' + self.current_table, fields, {f: data[f] for f in fields})
        if dlg.result:
            set_clause = ','.join(f'[{k}]=?' for k in dlg.result.keys())
            params = tuple(dlg.result.values())
            # find PK as first column ending with ID (simple heuristic)
            pk = next((c for c in cols if c.lower().endswith('id')), cols[0])
            pk_val = data[pk]
            sql = f"UPDATE {self.current_table} SET {set_clause} WHERE {pk}=?"
            try:
                self.db.execute(sql, params + (pk_val,))
                self.refresh()
            except Exception as e:
                messagebox.showerror('Error', str(e))

    def delete_record(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning('Select', 'Select a row first')
            return
        if not messagebox.askyesno('Confirm', 'Delete selected row?'):
            return
        vals = self.tree.item(sel)['values']
        cols = self.tree['columns']
        data = dict(zip(cols, vals))
        pk = next((c for c in cols if c.lower().endswith('id')), cols[0])
        pk_val = data[pk]
        sql = f"DELETE FROM {self.current_table} WHERE {pk}=?"
        try:
            self.db.execute(sql, (pk_val,))
            self.refresh()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def refresh(self):
        if self.current_table:
            self.load_table(self.current_table)

    # Admin actions
    def admin_create_login(self):
        from tkinter.simpledialog import askstring
        login = askstring('Create login', 'Login name:')
        pwd = askstring('Create login', 'Password:')
        if not login or not pwd: return
        try:
            from db import create_sql_login
            create_sql_login(self.db, login, pwd)
            messagebox.showinfo('OK', 'Login created (or error shown)')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def admin_create_db_user(self):
        from tkinter.simpledialog import askstring
        dbname = askstring('DB name', 'Database name:')
        login = askstring('Login name', 'Login name:')
        if not dbname or not login: return
        try:
            from db import create_db_user
            create_db_user(self.db, dbname, login)
            messagebox.showinfo('OK', 'DB user created')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def admin_add_user_role(self):
        from tkinter.simpledialog import askstring
        role = askstring('Role name', 'Role name:')
        user = askstring('User name', 'User name:')
        if not role or not user: return
        try:
            from db import add_user_to_role
            add_user_to_role(self.db, role, user)
            messagebox.showinfo('OK', 'User added to role')
        except Exception as e:
            messagebox.showerror('Error', str(e))
