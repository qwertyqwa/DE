import sqlite3

def init_db():
    conn = sqlite3.connect('bicycle_shop.db')
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        login TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    ''')
    
    # Таблица товаров
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        price REAL
    )
    ''')
    
    # Таблица заказов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        product_ids TEXT, -- список id товаров
        total REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    # Добавим тестовых пользователей
    cursor.execute("INSERT OR IGNORE INTO users (login, password, role) VALUES ('client', '123', 'client')")
    cursor.execute("INSERT OR IGNORE INTO users (login, password, role) VALUES ('manager', '123', 'manager')")
    cursor.execute("INSERT OR IGNORE INTO users (login, password, role) VALUES ('admin', '123', 'admin')")

    # Добавим тестовые товары
    cursor.execute("INSERT OR IGNORE INTO products (id, name, description, price) VALUES (1, 'Городской велосипед', 'Удобный городской велосипед', 15000)")
    cursor.execute("INSERT OR IGNORE INTO products (id, name, description, price) VALUES (2, 'Горный велосипед', 'Для езды по бездорожью', 30000)")

    conn.commit()
    conn.close()

init_db()
