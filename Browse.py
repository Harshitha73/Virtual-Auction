from tkinter import Tk, Label, Scrollbar, Button, ttk

import pymysql


class BrowsePage:
    def __init__(self, db_connection, is_seller=False):
        self.items = None
        self.root = Tk()
        self.root.title("Browse Items")
        self.root.geometry("600x400")

        self.db_connection = db_connection
        self.is_seller = is_seller

        self.label_heading = Label(self.root, text="Browse All Items", font=("Helvetica", 16))
        self.label_heading.pack(pady=10)

        self.scrollbar = Scrollbar(self.root)
        self.scrollbar.pack(side="right", fill="y")

        self.style = ttk.Style()
        self.style.theme_use("default")

        self.style.configure("Treeview.Heading", background="lightblue", foreground="black",
                             font=("Helvetica", 10, "bold"))
        self.style.map("Treeview", background=[("selected", "lightblue")])

        self.tree = ttk.Treeview(self.root, columns=("Item ID", "Name", "Description", "Type Name", "Seller ID"),
                                 show="headings", yscrollcommand=self.scrollbar.set)
        self.tree.column("Item ID", width=80, anchor="center")
        self.tree.column("Name", width=120, anchor="center")
        self.tree.column("Description", width=200, anchor="center")
        self.tree.column("Type Name", width=80, anchor="center")
        self.tree.column("Seller ID", width=80, anchor="center")

        self.tree.heading("Item ID", text="Item ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Type Name", text="Type Name")
        self.tree.heading("Seller ID", text="Seller ID")

        self.style.configure("Treeview.Cell", borderwidth=1, relief="solid")

        self.scrollbar = Scrollbar(self.root)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.pack(padx=10, pady=5, fill="both", anchor="center", expand=True)

        self.scrollbar.config(command=self.tree.yview)

        self.populate_items()

        if self.is_seller:
            cursor = self.db_connection.cursor()
            # query = "SELECT SellerID FROM Seller JOIN Users ON Users.EmailID = Seller.EmailID"
            # cursor.execute(query)
            cursor.callproc("seller_user_join")
            SellerID = cursor.fetchone()
            self.btn_back = Button(self.root, text="Back", command=lambda: self.open_products_page(SellerID))
            self.btn_back.pack(pady=5)
        else:
            cursor = self.db_connection.cursor()
            # query = "SELECT BidderID FROM Bidder JOIN Users ON Users.EmailID = Bidder.EmailID"
            # cursor.execute(query)
            cursor.callproc("bidder_user_join")
            BidderID = cursor.fetchone()
            print(BidderID)
            if self.items:
                self.btn_bid = Button(self.root, text="Place Bid", command=lambda: self.open_bid_page(BidderID))
                self.btn_bid.pack(pady=5)

        self.root.mainloop()

    def open_bid_page(self, BidderID):
        from Bid import BidPage
        BidPage(self.db_connection, BidderID)

    def open_products_page(self, SellerID):
        self.root.destroy()  # Destroy the current window
        from Products import ProductsPage
        ProductsPage(self.db_connection, SellerID)

    def populate_items(self):
        try:
            cursor = self.db_connection.cursor()

            cursor.callproc("get_items_all")
            self.items = cursor.fetchall()

            for item in self.items:
                self.tree.insert("", "end", values=item)

        except pymysql.err.OperationalError:
            print("Error:")
