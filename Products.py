from tkinter import Tk, Label, Entry, Text, Button, messagebox, StringVar, OptionMenu

import pymysql

from Bid import ViewBids


class ProductsPage:
    def __init__(self, db_connection, seller_id):
        self.master = Tk()
        self.master.title("")
        self.master.geometry("900x700")
        self.db_connection = db_connection
        self.seller_id = seller_id

        self.label_heading = Label(self.master, text="Welcome, choose one of the options", font=("Helvetica", 16))
        self.label_heading.pack(pady=10)

        self.btn_add = Button(self.master, text="Add Items", command=self.add_product)
        self.btn_add.pack(pady=10)

        self.btn_add_item_type = Button(self.master, text="Add ItemType", command=self.add_item_type)
        self.btn_add_item_type.pack(pady=5)

        self.btn_goto_browse = Button(self.master, text="Go to BrowsePage", command=self.goto_browse)
        self.btn_goto_browse.pack(pady=5)

        self.btn_view_bids = Button(self.master, text="Bids on Items", command=self.goto_view_bids)
        self.btn_view_bids.pack(pady=5)

        self.btn_logout = Button(self.master, text="Logout", command=self.logout)
        self.btn_logout.pack(pady=5)

        self.master.mainloop()

    def get_item_types(self):
        try:
            cursor = self.db_connection.cursor()
            # query = "SELECT ItemTypeID, Name FROM ItemType"
            # cursor.execute(query)
            cursor.callproc("get_item_types")
            item_types = cursor.fetchall()

            return [(item[0], item[1]) for item in item_types]

        except pymysql.err.OperationalError:
            messagebox.showerror("Error fetching item types:")
            return []

    def add_item_type(self):
        add_item_type_master = Tk()
        add_item_type_master.title("Add New Item Type")
        add_item_type_master.geometry("400x300")

        label_name = Label(add_item_type_master, text="Name:")
        label_name.pack()
        entry_name = Entry(add_item_type_master)
        entry_name.pack()

        label_description = Label(add_item_type_master, text="Description:")
        label_description.pack()
        entry_description = Text(add_item_type_master, height=4)
        entry_description.pack()

        def submit_item_type():
            name = entry_name.get().strip()
            description = entry_description.get("1.0", "end-1c").strip()

            if name and description:
                self.add_new_item_type(name, description)
                add_item_type_master.destroy()
            else:
                messagebox.showerror("Error", "Please fill in all fields!")

        btn_submit = Button(add_item_type_master, text="Submit", command=submit_item_type)
        btn_submit.pack(pady=10)

        add_item_type_master.mainloop()

    def add_new_item_type(self, name, description):
        try:
            cursor = self.db_connection.cursor()
            # insert_query = "INSERT INTO ItemType (Name, Description) VALUES (%s, %s)"
            # cursor.execute(insert_query, (name, description))
            cursor.callproc("insert_item_type", [name, description])
            self.db_connection.commit()
            messagebox.showinfo("Success", "Item type added successfully!")

        except pymysql.err.OperationalError:
            messagebox.showerror("Error adding item type")

    def add_product(self):
        self.master.destroy()
        self.master.quit()
        AddProductPage(self.db_connection, self.seller_id, self.get_item_types())

    def goto_browse(self):
        self.master.destroy()
        self.master.quit()
        from Browse import BrowsePage
        BrowsePage(self.db_connection, True)

    def logout(self):
        self.master.destroy()
        self.master.quit()
        import Auction
        Auction.ChooseOptionPage()

    def goto_view_bids(self):
        self.master.destroy()
        self.master.quit()
        cursor = self.db_connection.cursor()
        # query = "SELECT SellerID FROM Seller JOIN Users ON Users.EmailID = Seller.EmailID"
        # cursor.execute(query)
        cursor.callproc("view_bid")
        SellerID = cursor.fetchone()
        ViewBids(self.db_connection, SellerID)


class AddProductPage:
    def __init__(self, db_connection, seller_id, item_types):
        self.master = Tk()
        self.master.title("Add Product")
        self.master.geometry("400x300")
        self.db_connection = db_connection
        self.seller_id = seller_id
        self.item_types = item_types if item_types else [('Select',)]
        self.sold = 0

        self.label_heading = Label(self.master, text="Add Product", font=("Helvetica", 16))
        self.label_heading.pack(pady=10)

        self.label_name = Label(self.master, text="Name:")
        self.label_name.pack()
        self.entry_name = Entry(self.master)
        self.entry_name.pack()

        self.label_description = Label(self.master, text="Description:")
        self.label_description.pack()
        self.entry_description = Text(self.master, height=4)
        self.entry_description.pack()

        self.label_item_type = Label(self.master, text="Item Type:")
        self.label_item_type.pack()

        self.selected_item_type = StringVar(self.master)
        self.selected_item_type.set('')  # Set default value

        self.item_type_var = OptionMenu(self.master, self.selected_item_type, *self.item_types)
        self.item_type_var.pack()

        self.btn_add = Button(self.master, text="Add Product", command=self.add_product_action)
        self.btn_add.pack(pady=10)

        self.btn_back = Button(self.master, text="Back", command=self.back_to_products)
        self.btn_back.pack(pady=10)

        self.master.mainloop()

    def add_product_action(self):
        name = self.entry_name.get().strip()
        description = self.entry_description.get("1.0", "end-1c").strip()

        if not name or not description or not self.selected_item_type.get():
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        item_type_string = self.selected_item_type.get().replace('(', '').split(',')[0].strip()
        item_type_id = int(item_type_string)

        try:
            cursor = self.db_connection.cursor()

            # insert_query = "INSERT INTO Item (Name, Description, ItemTypeID, SellerID, Sold) VALUES (%s, %s, %s, %s, %s)"
            # cursor.execute(insert_query, (name, description, item_type_id, self.seller_id, self.sold))
            cursor.callproc("insert_item", [name, description, item_type_id, self.seller_id, self.sold])
            self.db_connection.commit()

            # ItemID = cursor.lastrowid()

            #cursor.execute("SELECT LAST_INSERT_ID()")
            cursor.callproc("get_last_insert_id")
            row = cursor.fetchone()
            ItemID = row[0] if row else 0

            # insert_sells_query = "INSERT INTO Sells (SellerID, ItemID) VALUES (%s, %s)"
            # cursor.execute(insert_sells_query, (self.seller_id, ItemID))
            # print(ItemID)
            cursor.callproc("insert_into_sells", [self.seller_id, ItemID])
            self.db_connection.commit()
            messagebox.showinfo("Success", "Product added successfully!")

        except pymysql.err.OperationalError:
            messagebox.showerror("Error adding product:")

    def back_to_products(self):
        self.master.destroy()
        self.master.quit()
        ProductsPage(self.db_connection, self.seller_id)
