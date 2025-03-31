import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time

# Connect to the database
connection = sqlite3.connect('barcode.db')
cursor = connection.cursor()

# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Smapca (
        Barcode TEXT UNIQUE,
        Name TEXT,
        Image BLOB,
        Price REAL,
        Description TEXT
    )
''')

last_insert_time = 0  # Cooldown variable

def show_all_products():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT Barcode, Name, Price, Description FROM Smapca")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

def insert_product():
    global last_insert_time
    barcode = barcode_entry.get().strip()
    name = name_entry.get().strip()
    price = price_entry.get().strip()
    description = description_entry.get().strip()
    image_path = image_path_label.cget("text")
    if not barcode or not name or not price or not description or image_path == "No file selected":
        messagebox.showerror("Input Error", "All fields are required!")
        return
    
    current_time = time.time()
    if current_time - last_insert_time < 1:
        return
    last_insert_time = current_time

    try:
        price = float(price)
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        cursor.execute('''INSERT INTO Smapca (Barcode, Name, Image, Price, Description) VALUES (?, ?, ?, ?, ?)''', (barcode, name, image_data, price, description))
        connection.commit()
        messagebox.showinfo("Success", f"Product '{name}' added successfully!")
        clear_inputs()
        show_all_products()
    except ValueError:
        messagebox.showerror("Input Error", "Invalid price!")
    except FileNotFoundError:
        messagebox.showerror("File Error", "Image file not found!")

def browse_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if file_path:
        image_path_label.config(text=file_path)

def clear_inputs():
    barcode_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    image_path_label.config(text="No file selected")

def search_product():
    barcode = barcode_entry.get().strip()
    if not barcode:
        messagebox.showerror("Search Error", "Please enter a barcode to search!")
        return
    cursor.execute("SELECT Name, Price, Description FROM Smapca WHERE Barcode=?", (barcode,))
    result = cursor.fetchone()
    if result:
        name_entry.delete(0, tk.END)
        name_entry.insert(0, result[0])
        price_entry.delete(0, tk.END)
        price_entry.insert(0, str(result[1]))
        description_entry.delete(0, tk.END)
        description_entry.insert(0, result[2])
    else:
        messagebox.showerror("Not Found", "No product found with this barcode!")

def update_product():
    barcode = barcode_entry.get().strip()
    name = name_entry.get().strip()
    price = price_entry.get().strip()
    description = description_entry.get().strip()
    if not barcode:
        messagebox.showerror("Update Error", "Enter a barcode to update!")
        return
    try:
        price = float(price)
        cursor.execute('''UPDATE Smapca SET Name=?, Price=?, Description=? WHERE Barcode=?''', (name, price, description, barcode))
        if cursor.rowcount:
            connection.commit()
            messagebox.showinfo("Update Success", f"Product '{name}' updated successfully!")
            show_all_products()
        else:
            messagebox.showerror("Update Error", "Barcode not found!")
    except ValueError:
        messagebox.showerror("Input Error", "Invalid price!")

def delete_product():
    barcode = barcode_entry.get().strip()
    if not barcode:
        messagebox.showerror("Delete Error", "Enter a barcode to delete!")
        return
    cursor.execute("DELETE FROM Smapca WHERE Barcode=?", (barcode,))
    if cursor.rowcount:
        connection.commit()
        clear_inputs()
        show_all_products()
        messagebox.showinfo("Delete Success", "Product deleted successfully!")
    else:
        messagebox.showerror("Delete Error", "Barcode not found!")

# GUI Setup
root = tk.Tk()
root.title("Product Management System")

# Entry fields
tk.Label(root, text="Barcode:").grid(row=0, column=0)
barcode_entry = tk.Entry(root)
barcode_entry.grid(row=0, column=1)
tk.Label(root, text="Name:").grid(row=1, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=1, column=1)
tk.Label(root, text="Price:").grid(row=2, column=0)
price_entry = tk.Entry(root)
price_entry.grid(row=2, column=1)
tk.Label(root, text="Description:").grid(row=3, column=0)
description_entry = tk.Entry(root)
description_entry.grid(row=3, column=1)

# Buttons
tk.Button(root, text="Select Image", command=browse_image).grid(row=4, column=0)
image_path_label = tk.Label(root, text="No file selected", fg="gray")
image_path_label.grid(row=4, column=1)
tk.Button(root, text="Add Product", command=insert_product).grid(row=5, column=0)
tk.Button(root, text="Search", command=search_product).grid(row=5, column=1)
tk.Button(root, text="Update", command=update_product).grid(row=6, column=0)
tk.Button(root, text="Delete", command=delete_product).grid(row=6, column=1)
tk.Button(root, text="Show All", command=show_all_products).grid(row=7, column=0, columnspan=2)

# Treeview
columns = ("Barcode", "Name", "Price", "Description")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.grid(row=8, column=0, columnspan=2)

show_all_products()
root.mainloop()
connection.close()
