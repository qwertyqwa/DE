import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Объект соединения
conn = sqlite3.connect('bicycle_shop.db')

# Глобальные переменные
current_user_role = None
current_user_id = None

# Функция авторизации
def login():
    global current_user_role, current_user_id
    login_input = entry_login.get()
    password_input = entry_password.get()

    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM users WHERE login=? AND password=?", (login_input, password_input))
    result = cursor.fetchone()
    if result:
        current_user_id, current_user_role = result
        messagebox.showinfo("Успех", f"Вход выполнен. Роль: {current_user_role}")
        login_frame.pack_forget()
        show_main_screen()
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

# Входное окно
def create_login_window():
    global login_frame, entry_login, entry_password
    login_frame = tk.Frame(root)
    login_frame.pack(pady=50)

    tk.Label(login_frame, text="Логин:").grid(row=0, column=0, pady=5)
    entry_login = tk.Entry(login_frame)
    entry_login.grid(row=0, column=1, pady=5)

    tk.Label(login_frame, text="Пароль:").grid(row=1, column=0, pady=5)
    entry_password = tk.Entry(login_frame, show='*')
    entry_password.grid(row=1, column=1, pady=5)

    btn_login = tk.Button(login_frame, text="Войти", command=login)
    btn_login.grid(row=2, column=0, columnspan=2, pady=10)

    btn_guest = tk.Button(login_frame, text="Гость", command=enter_guest)
    btn_guest.grid(row=3, column=0, columnspan=2, pady=5)

def enter_guest():
    global current_user_role, current_user_id
    current_user_role = 'guest'
    current_user_id = None
    login_frame.pack_forget()
    show_main_screen()

# Основное окно
root = tk.Tk()
root.title("ООО 'ВелосипедДрайв'")
root.geometry("800x600")
create_login_window()

# Функция отображения главного экрана
def show_main_screen():
    global main_frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Создаем таблицу товаров
    columns = ('id', 'name', 'description', 'price')
    tree = ttk.Treeview(main_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col.capitalize())
    tree.pack(fill=tk.BOTH, expand=True)

    load_products(tree)

    # В зависимости от роли показываем кнопки управления
    if current_user_role in ('manager', 'admin'):
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=10)

        btn_refresh = tk.Button(btn_frame, text="Обновить", command=lambda: load_products(tree))
        btn_refresh.pack(side=tk.LEFT, padx=5)
        if current_user_role == 'admin':
            btn_add = tk.Button(btn_frame, text="Добавить товар", command=lambda: open_product_form(tree))
            btn_add.pack(side=tk.LEFT, padx=5)
            btn_edit = tk.Button(btn_frame, text="Редактировать", command=lambda: edit_product(tree))
            btn_edit.pack(side=tk.LEFT, padx=5)
            btn_delete = tk.Button(btn_frame, text="Удалить", command=lambda: delete_product(tree))
            btn_delete.pack(side=tk.LEFT, padx=5)
    elif current_user_role == 'client':
        # Можно добавить дополнительные кнопки для клиента
        pass
    elif current_user_role == 'guest':
        # Только просмотр
        pass

def load_products(tree):
    for row in tree.get_children():
        tree.delete(row)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price FROM products")
    for product in cursor.fetchall():
        tree.insert('', tk.END, values=product)

def open_product_form(tree):
    form = tk.Toplevel(root)
    form.title("Добавление товара")

    tk.Label(form, text="Название:").grid(row=0, column=0)
    name_entry = tk.Entry(form)
    name_entry.grid(row=0, column=1)

    tk.Label(form, text="Описание:").grid(row=1, column=0)
    desc_entry = tk.Entry(form)
    desc_entry.grid(row=1, column=1)

    tk.Label(form, text="Цена:").grid(row=2, column=0)
    price_entry = tk.Entry(form)
    price_entry.grid(row=2, column=1)

    def add_product():
        name = name_entry.get()
        desc = desc_entry.get()
        try:
            price = float(price_entry.get())
        except:
            messagebox.showerror("Ошибка", "Некорректная цена")
            return
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
                       (name, desc, price))
        conn.commit()
        load_products(tree)
        form.destroy()

    btn_save = tk.Button(form, text="Сохранить", command=add_product)
    btn_save.grid(row=3, column=0, columnspan=2, pady=10)

def edit_product(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите товар")
        return
    item = tree.item(selected_item)
    product_id = item['values'][0]

    form = tk.Toplevel(root)
    form.title("Редактирование товара")

    cursor = conn.cursor()
    cursor.execute("SELECT name, description, price FROM products WHERE id=?", (product_id,))
    name, desc, price = cursor.fetchone()

    tk.Label(form, text="Название:").grid(row=0, column=0)
    name_entry = tk.Entry(form)
    name_entry.insert(0, name)
    name_entry.grid(row=0, column=1)

    tk.Label(form, text="Описание:").grid(row=1, column=0)
    desc_entry = tk.Entry(form)
    desc_entry.insert(0, desc)
    desc_entry.grid(row=1, column=1)

    tk.Label(form, text="Цена:").grid(row=2, column=0)
    price_entry = tk.Entry(form)
    price_entry.insert(0, str(price))
    price_entry.grid(row=2, column=1)

    def save_changes():
        new_name = name_entry.get()
        new_desc = desc_entry.get()
        try:
            new_price = float(price_entry.get())
        except:
            messagebox.showerror("Ошибка", "Некорректная цена")
            return
        cursor.execute("UPDATE products SET name=?, description=?, price=? WHERE id=?",
                       (new_name, new_desc, new_price, product_id))
        conn.commit()
        load_products(tree)
        form.destroy()

    btn_save = tk.Button(form, text="Сохранить", command=save_changes)
    btn_save.grid(row=3, column=0, columnspan=2, pady=10)

def delete_product(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите товар")
        return
    item = tree.item(selected_item)
    product_id = item['values'][0]

    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    load_products(tree)

# Запуск окна
root.mainloop()