# db.py - database utility functions using pyodbc
import pyodbc

class DBConnection:
    def __init__(self):
        self.conn_str = None
        self.conn = None

    def build_conn_str(self, server, database, driver, uid=None, pwd=None, trusted=False, timeout=5):
        # Example: DRIVER={ODBC Driver 17 for SQL Server};SERVER=server;DATABASE=db;UID=user;PWD=pwd;TrustServerCertificate=yes
        parts = [f"DRIVER={{{driver}}}", f"SERVER={server}", f"DATABASE={database}", "TrustServerCertificate=yes"]
        if trusted:
            parts.append("Trusted_Connection=yes")
        else:
            parts.append(f"UID={uid}")
            parts.append(f"PWD={pwd}")
        self.conn_str = ";".join(parts)
        return self.conn_str

    def test_connection(self):
        if not self.conn_str:
            raise ValueError('Строка подключения не задана')
        try:
            conn = pyodbc.connect(self.conn_str, timeout=5)
            conn.close()
            return True, 'Успешное подключение'
        except Exception as e:
            return False, str(e)

    def connect(self):
        if not self.conn_str:
            raise ValueError('Строка подключения не задана')
        self.conn = pyodbc.connect(self.conn_str)
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    # CRUD helpers
    def fetch_all(self, table):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
        return cols, rows

    def execute(self, sql, params=None):
        cur = self.conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        try:
            self.conn.commit()
        except:
            pass
        return cur

# Admin helpers (be careful: these require sysadmin or appropriate permissions)
def create_sql_login(dbconn: DBConnection, login_name, password):
    sql = f"""IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = '{login_name}')
BEGIN
    CREATE LOGIN [{login_name}] WITH PASSWORD = '{password}';
END
ELSE
BEGIN
    RAISERROR('Login already exists',16,1);
END"""
    return dbconn.execute(sql)

def create_db_user(dbconn: DBConnection, dbname, login_name, user_name=None):
    if not user_name:
        user_name = login_name

    sql = f"""
    USE [{dbname}];
    IF NOT EXISTS (
        SELECT * FROM sys.database_principals WHERE name = '{user_name}'
    )
    BEGIN
        CREATE USER [{user_name}] FOR LOGIN [{login_name}];
    END
    """
    return dbconn.execute(sql)

def add_user_to_role(dbconn: DBConnection, role_name, user_name):
    sql = f"ALTER ROLE [{role_name}] ADD MEMBER [{user_name}];"
    return dbconn.execute(sql)
