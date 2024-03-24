from tkinter import Tk, Label, Button, Entry, messagebox

import pymysql


class PaymentPage:
    def __init__(self, db_connection, bidder_id, item_id):
        self.item_id = item_id
        self.add_card_window = None
        self.card_number = 0
        self.master = Tk()
        self.master.title("Payment Details")
        self.master.geometry("400x300")
        self.db_connection = db_connection
        self.bidder_id = bidder_id

        self.label_heading = Label(self.master, text="Credit Card Details", font=("Helvetica", 16))
        self.label_heading.pack(pady=10)

        self.display_credit_card_details()

    def display_credit_card_details(self):
        try:
            cursor = self.db_connection.cursor()

            # Fetch credit card number and name for the bidder from the database
            # cursor.execute("SELECT CreditCardNumber, NameOnCard FROM CreditCard WHERE BidderID = %s", (self.bidder_id,))
            cursor.callproc("fetch_card_and_bidder", [self.bidder_id])
            credit_card_details = cursor.fetchall()

            for card_details in credit_card_details:
                self.card_number, name_on_card = card_details

                # Display credit card number and name
                card_label = Label(self.master, text=f"Card Number: {self.card_number}\nName on Card: {name_on_card}")
                card_label.pack()
                # if credit_card_details:
                use_button = Button(self.master, text="Use", command=self.use_existing_card)
                use_button.pack(pady=5)

                delete_button = Button(self.master, text="Delete", command=self.delete_card)
                delete_button.pack(pady=5)

            add_new_button = Button(self.master, text="Add New Card", command=self.add_new_card)
            add_new_button.pack(pady=10)

        except pymysql.err.OperationalError as e:
            print("Error occurred while fetching credit card details:", e)

    def delete_card(self):
        try:
            cursor = self.db_connection.cursor()

            # Delete the credit card details from the database
            # cursor.execute("DELETE FROM CreditCard WHERE CreditCardNumber = %s", (self.card_number,))
            cursor.callproc("delete_credit_card", [self.card_number])
            self.db_connection.commit()

            messagebox.showinfo("Card Deleted", "Credit card details deleted successfully!")
            self.master.after(3000, self.refresh_payment_page)

        except pymysql.err.OperationalError as e:
            print("Error occurred while deleting credit card details:", e)
            messagebox.showerror("Deletion Error", "Failed to delete credit card details.")

    def refresh_payment_page(self):
        self.master.destroy()
        PaymentPage(self.db_connection, self.bidder_id, self.item_id)

    def use_existing_card(self):

        try:
            cursor = self.db_connection.cursor()

            # Fetch the bid amount, item ID, and seller ID based on bidder ID
            # cursor.execute(
            #    "SELECT b.BidAmount, i.ItemID, i.SellerID FROM Bid b JOIN Item i ON b.ItemID = i.ItemID WHERE b.BidderID = %s",
            #    (self.bidder_id,))
            cursor.callproc("fetch_details_for_transaction", [self.bidder_id, self.item_id])
            bid_details = cursor.fetchone()

            if bid_details:
                bid_amount, item_id, seller_id = bid_details

                # Insert a new transaction entry
                # cursor.execute(
                #    "INSERT INTO Transaction (Amount, BidderID, SellerID, ItemID, CreditCardNumber) VALUES (%s, %s, %s, %s, %s)",
                #    (bid_amount, self.bidder_id, seller_id, item_id, self.card_number)
                # )

                cursor.callproc("insert_into_transaction",
                                [bid_amount, self.bidder_id, seller_id, item_id, self.card_number])
                self.db_connection.commit()

                # Update the Buys table to reflect the purchase
                # cursor.execute(
                #    "INSERT INTO Buys (ItemID, BidderID) VALUES (%s, %s)",
                #    (item_id, self.bidder_id)
                # )
                cursor.callproc("insert_into_buys", [item_id, self.bidder_id])
                self.db_connection.commit()

                messagebox.showinfo("Payment Successful", "Payment done for the bid amount!")
                self.master.after(2000, self.refresh_notifications_page)  # Refresh notifications after 2 seconds
            else:
                messagebox.showerror("Bid Not Found", "No bid found for this bidder.")

        except Exception as e:
            print("Payment error:", e)
            messagebox.showerror("Payment Error", "Payment failed. Please try again.")

    def add_new_card(self):
        # Logic to add a new card for payment
        def save_card_details():
            card_number = entry_card_number.get()
            expiry_date = entry_expiry_date.get()
            name_on_card = entry_name_on_card.get()
            card_type = entry_card_type.get()

            if card_number and expiry_date and name_on_card and card_type:
                try:
                    cursor = self.db_connection.cursor()

                    # Insert the new credit card details into the database
                    # cursor.execute(
                    #    "INSERT INTO CreditCard (CreditCardNumber, ExpiryDate, NameOnCard, CardType, BidderID) VALUES (%s, %s, %s, %s, %s)",
                    #    (card_number, expiry_date, name_on_card, card_type, self.bidder_id)
                    # )
                    cursor.callproc("insert_new_credit_card",
                                    [card_number, expiry_date, name_on_card, card_type, self.bidder_id])
                    self.db_connection.commit()

                    # Notify user that the card details have been saved
                    save_label.config(text="Card details saved successfully!", fg="green")
                    self.master.after(3000, self.go_back_to_previous_page)

                except pymysql.err.OperationalError as e:
                    print("Error occurred while saving credit card details:", e)
                    save_label.config(text="Error occurred while saving card details", fg="red")

        # Create a new window for entering new card details
        self.add_card_window = Tk()
        self.add_card_window.title("Add New Card")
        self.add_card_window.geometry("400x300")

        label_card_number = Label(self.add_card_window, text="Card Number:")
        label_card_number.pack()

        entry_card_number = Entry(self.add_card_window)
        entry_card_number.pack()

        label_expiry_date = Label(self.add_card_window, text="Expiry Date (YYYY-MM-DD):")
        label_expiry_date.pack()

        entry_expiry_date = Entry(self.add_card_window)
        entry_expiry_date.pack()

        label_name_on_card = Label(self.add_card_window, text="Name on Card:")
        label_name_on_card.pack()

        entry_name_on_card = Entry(self.add_card_window)
        entry_name_on_card.pack()

        label_card_type = Label(self.add_card_window, text="Card Type:")
        label_card_type.pack()

        entry_card_type = Entry(self.add_card_window)
        entry_card_type.pack()

        save_button = Button(self.add_card_window, text="Save", command=save_card_details)
        save_button.pack()

        save_label = Label(self.add_card_window, text="")
        save_label.pack()

        self.add_card_window.mainloop()

    def update_transactions(self):
        try:

            # Your code to update transaction and buys tables...
            # Update transactions and buys tables based on the successful payment

            # For demonstration, let's assume the update was successful
            messagebox.showinfo("Payment Successful", "Payment done for the bid amount!")
            self.master.after(2000, self.refresh_notifications_page)  # Refresh notifications after 2 seconds

        except pymysql.err.OperationalError as e:
            print("Error updating transactions:", e)
            messagebox.showerror("Transaction Update Error", "Failed to update transactions. Please try again.")

    def refresh_notifications_page(self):
        self.master.destroy()
        from Notifications import NotificationsPage
        NotificationsPage(self.db_connection, self.bidder_id)

    def go_back_to_previous_page(self):
        self.master.destroy()
        self.add_card_window.destroy()
        from Notifications import NotificationsPage
        NotificationsPage(self.db_connection, self.bidder_id)
