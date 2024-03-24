from tkinter import Tk, Label, StringVar, OptionMenu, messagebox, Button

import pymysql


class HighestBidPage:
    def __init__(self, db_connection, seller_id):
        self.btn_declare_winner = None
        self.item = 0
        self.master = Tk()
        self.master.title("Get Highest Bids")
        self.master.geometry("900x700")
        self.db_connection = db_connection
        self.seller_id = seller_id

        self.label_heading = Label(self.master, text="Get Highest Bids", font=("Helvetica", 16))
        self.label_heading.pack(pady=10)

        self.selected_item = StringVar(self.master)
        self.selected_item.set('')  # Set default value

        items = self.get_items()
        if items:
            self.label_item = Label(self.master, text="Item:")
            self.label_item.pack()
            self.item_var = OptionMenu(self.master, self.selected_item, *items)
            self.item_var.pack()
            self.btn_add = Button(self.master, text="Find", command=self.display_highest_bid)
            self.btn_add.pack(pady=10)

        self.result_label = Label(self.master, text="")
        self.result_label.pack()

        self.btn_back = Button(self.master, text="Back", command=self.back_to_view_bid)
        self.btn_back.pack(pady=10)

        self.master.mainloop()

    def get_items(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.callproc('item_seller')
            items = cursor.fetchall()
            if not items:
                messagebox.showinfo("No Items", "All your items are sold!")
            return [(item[0], item[1]) for item in items]

        except pymysql.err.OperationalError:
            messagebox.showerror("Error fetching items: ")
            return []

    def get_highest_bid(self, chosen_item):
        try:
            cursor = self.db_connection.cursor()
            cursor.callproc("get_highest_bid", [chosen_item])
            highest_bid = cursor.fetchone()
            if str(highest_bid[0]) == "None":
                return "0"
            return highest_bid

        except pymysql.err.OperationalError as e:
            print("Error fetching highest bid:", e)

    def display_highest_bid(self):
        self.item = int(self.selected_item.get().replace('(', '').split(',')[0].strip())
        if self.item:
            highest_bid = float(self.get_highest_bid(self.item)[0])

            if highest_bid is not None:
                self.result_label.config(text=f"Highest Bid: {str(highest_bid)}")
                if highest_bid != 0.0:
                    self.btn_declare_winner = Button(self.master, text="Declare Winner", command=self.declare_winner)
                    self.btn_declare_winner.pack(pady=10)
            else:
                self.result_label.config(text="No bid found for this item.")
        else:
            self.result_label.config(text="Please select an item.")

    def back_to_view_bid(self):
        self.master.destroy()
        self.master.quit()
        from Bid import ViewBids
        ViewBids(self.db_connection, self.seller_id)

    def declare_winner(self):
        try:
            cursor = self.db_connection.cursor()

            # Update Item table to mark the item as sold
            cursor.callproc("set_item_to_sold", [self.item])

            cursor.callproc("get_highest_bid_id", [self.item])
            highest_bid_id = cursor.fetchone()

            # Retrieve the bidder ID who placed the highest bid
            cursor.callproc("get_highest_bidder_id_query", [highest_bid_id[0]])
            winner_bidder_id = cursor.fetchone()

            if winner_bidder_id:
                # Insert the winning bid details into the WinningBid table

                cursor.callproc("insert_winning_bid", [self.item, winner_bidder_id[0], highest_bid_id[0]])

                self.db_connection.commit()

                messagebox.showerror("Message", "Winner will be notified")
                self.master.quit()
                self.back_to_view_bid()
            else:
                messagebox.showerror("Error", "No winning bidder found for this item.")

        except pymysql.err.OperationalError:
            messagebox.showerror("Error declaring the winner")
