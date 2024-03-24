from tkinter import Tk, Label, Entry, Button, messagebox, StringVar, OptionMenu, Scrollbar, ttk

import pymysql


class BidPage:
    def __init__(self, db_connection, bidder_id):
        self.db_connection = db_connection
        self.bidder_id = bidder_id

        self.bid_window = Tk()
        self.bid_window.title("Place Bid")
        self.bid_window.geometry("900x700")

        self.label_heading = Label(self.bid_window, text="Place Bid", font=("Helvetica", 16))
        self.label_heading.pack(pady=10)

        self.label_item = Label(self.bid_window, text="Select Item:")
        self.label_item.pack()

        self.selected_item = StringVar(self.bid_window)
        self.selected_item.set('')  # Set default value

        self.item_types = self.get_available_items()
        self.item_dropdown = OptionMenu(self.bid_window, self.selected_item, *self.item_types)
        self.item_dropdown.pack()

        self.label_amount = Label(self.bid_window, text="Bid Amount:")
        self.label_amount.pack()
        self.entry_amount = Entry(self.bid_window)
        self.entry_amount.pack()

        self.btn_submit = Button(self.bid_window, text="Submit Bid", command=self.submit_bid)
        self.btn_submit.pack(pady=10)

        self.btn_cancel = Button(self.bid_window, text="Cancel", command=self.cancel_bid)
        self.btn_cancel.pack(pady=10)

        self.bid_window.mainloop()

    def cancel_bid(self):
        self.bid_window.destroy()

    def get_available_items(self):
        try:
            cursor = self.db_connection.cursor()
            # query = "SELECT ItemID, Name FROM Item"
            # cursor.execute(query)
            cursor.callproc("get_items")
            items = cursor.fetchall()
            return [(item[0], item[1]) for item in items]
        except pymysql.err.OperationalError:
            print("Error")
            return []

    def submit_bid(self):
        amount = self.entry_amount.get().strip()
        if amount and self.selected_item.get():
            try:
                bid_amount = float(amount)
                item_id = int(self.selected_item.get().replace('(', '').split(',')[0].strip())
                print(self.bidder_id)
                bidder_id = int(self.bidder_id[0][0])
                print(self.bidder_id[0])
                cursor = self.db_connection.cursor()

                # query = "INSERT INTO Bid (BidAmount, ItemID, BidderID) VALUES (%s, %s, %s)"
                # cursor.execute(query, (bid_amount, item_id, bidder_id))
                cursor.callproc("insert_bid", [bid_amount, item_id, bidder_id])
                self.db_connection.commit()
                messagebox.showinfo("Success", "Bid placed successfully!")
                self.bid_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid bid amount.")
            except pymysql.err.OperationalError:
                messagebox.showerror("Error placing bid:")
        else:
            messagebox.showerror("Error", "Please fill in all fields.")


class ViewBids:
    def __init__(self, db_connection, seller_id):
        self.db_connection = db_connection
        self.seller_id = seller_id

        self.bid_window = Tk()
        self.bid_window.title("Bids")
        self.bid_window.geometry("900x700")

        self.label_heading = Label(self.bid_window, text="Bids on all your items", font=("Helvetica", 16))
        self.label_heading.pack(pady=10)

        self.scrollbar = Scrollbar(self.bid_window)
        self.scrollbar.pack(side="right", fill="y")

        self.style = ttk.Style()
        self.style.theme_use("default")

        self.style.configure("Treeview.Heading", background="lightblue", foreground="black",
                             font=("Helvetica", 10, "bold"))
        self.style.map("Treeview", background=[("selected", "lightblue")])

        self.tree = ttk.Treeview(self.bid_window, columns=("Item ID", "Item Name", "Bid Amount", "Bidder Name"),
                                 show="headings", yscrollcommand=self.scrollbar.set)
        self.tree.column("Item ID", width=80, anchor="center")
        self.tree.column("Item Name", width=120, anchor="center")
        self.tree.column("Bid Amount", width=200, anchor="center")
        self.tree.column("Bidder Name", width=80, anchor="center")

        self.tree.heading("Item ID", text="Item ID")
        self.tree.heading("Item Name", text="Item Name")
        self.tree.heading("Bid Amount", text="Bid Amount")
        self.tree.heading("Bidder Name", text="Bidder Name")

        self.style.configure("Treeview.Cell", borderwidth=1, relief="solid")

        self.scrollbar = Scrollbar(self.bid_window)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.pack(padx=10, pady=5, fill="both", anchor="center", expand=True)

        self.scrollbar.config(command=self.tree.yview)

        self.btn_highest_bid = Button(self.bid_window, text="Get highest Bids", command=self.goto_highest_bids)
        self.btn_highest_bid.pack(pady=10)

        self.btn_back = Button(self.bid_window, text="Back", command=self.back_to_products)
        self.btn_back.pack(pady=10)

        self.populate_items()
        self.bid_window.mainloop()

    def populate_items(self):
        try:
            cursor = self.db_connection.cursor()
            # query = "SELECT item.ItemID, item.Name, bid.BidAmount, concat(bidder.FirstName, ' ', bidder.LastName) AS 'Bidder Name' FROM item JOIN bid JOIN bidder;"
            # cursor.execute(query)
            cursor.callproc("join_bid_bidder", [self.seller_id])
            items = cursor.fetchall()

            for item in items:
                self.tree.insert("", "end", values=item)

        except pymysql.err.OperationalError:
            print("Error:")

        self.bid_window.mainloop()

    def back_to_products(self):
        self.bid_window.destroy()
        from Products import ProductsPage
        ProductsPage(self.db_connection, self.seller_id)

    def goto_highest_bids(self):
        self.bid_window.destroy()

        from HighestBid import HighestBidPage
        HighestBidPage(self.db_connection, self.seller_id)
