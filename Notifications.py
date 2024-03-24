from tkinter import Tk, Label, Button, Frame

import pymysql


class NotificationsPage:
    def __init__(self, db_connection, BidderID):
        self.master = Tk()
        self.master.title("Notifications")
        self.master.geometry("800x600")

        self.db_connection = db_connection
        self.BidderID = BidderID

        self.label_heading = Label(self.master, text="Notifications", font=("Helvetica", 16))
        self.label_heading.pack(pady=10)

        self.notification_frame = Frame(self.master)
        self.notification_frame.pack(padx=10, pady=10)

        self.display_winning_items()

    def display_winning_items(self):
        try:
            cursor = self.db_connection.cursor()
            # query = "SELECT wb.ItemID, i.Name, i.Description, i.SellerID, b.BidAmount FROM WinningBid wb JOIN Item i ON wb.ItemID = i.ItemID JOIN Bid b ON wb.HighestBidID = b.BidID WHERE wb.WinnerBidderID = %s"
            # cursor.execute(query, (self.BidderID,))
            cursor.callproc("get_winning_items", [self.BidderID])
            winning_items = cursor.fetchall()

            for item in winning_items:
                item_id, item_name, item_desc, seller_id, bid_amount = item

                # Fetch seller details
                seller_details = self.fetch_seller_details(seller_id)

                # Create a frame for item details and pay button
                item_frame = Frame(self.notification_frame, borderwidth=2, relief="solid")
                item_frame.pack(padx=20, pady=5, fill="x")

                # Label for item details
                item_label = Label(
                    item_frame,
                    text=f"Item ID: {item_id}\nName: {item_name}\nDescription: {item_desc}\nAmount: {bid_amount}\nSeller: {seller_details}",
                    padx=10,
                    pady=10,
                )
                item_label.pack(side="left")

                # Pay button
                accept_button = Button(
                    item_frame,
                    text="Pay",
                    command=lambda id=item_id: self.pay_amount(id),
                    padx=5,
                    pady=5,
                )
                accept_button.pack(side="right")

        except pymysql.err.OperationalError as e:
            print("Error occurred while fetching winning items:", e)

    def fetch_seller_details(self, seller_id):
        try:
            cursor = self.db_connection.cursor()
            # query = "SELECT FirstName, LastName, EmailID FROM Seller WHERE SellerID = %s"
            # cursor.execute(query, (seller_id,))
            cursor.callproc("get_seller_details", [seller_id])
            seller_details = cursor.fetchone()

            if seller_details:
                return f"{seller_details[0]} {seller_details[1]} ({seller_details[2]})"
            else:
                return "Seller details not found"

        except pymysql.err.OperationalError as e:
            print("Error occurred while fetching seller details:", e)

    def pay_amount(self, item_id):
        self.master.destroy()

        # Create an instance of PaymentPage with the bidder ID
        from Payment import PaymentPage
        PaymentPage(self.db_connection, self.BidderID, item_id)
