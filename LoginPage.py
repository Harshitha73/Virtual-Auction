from tkinter import Label, Entry, Button, messagebox, Tk, Toplevel

import pymysql
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def check_user_type(email, cursor):
    cursor.callproc("get_seller_for_email", [email])
    seller_result = cursor.fetchone()
    cursor.callproc("get_bidder_for_email", [email])
    bidder_result = cursor.fetchone()
    if seller_result:
        return "Seller", seller_result[1], seller_result[0], seller_result[2]
    elif bidder_result:
        return "Bidder", bidder_result[1], bidder_result[0], bidder_result[2]  # First name of the bidder
    else:
        return "Unknown", None  # No match found for seller or bidder


def goto_browse(db_connection):
    from Browse import BrowsePage
    BrowsePage(db_connection)


def goto_notifications(db_connection, BidderID):
    from Notifications import NotificationsPage
    NotificationsPage(db_connection, BidderID)


class LoginPage:
    def __init__(self, master):
        self.btn_purchases = None
        self.btn_notifications = None
        self.btn_logout = None
        self.btn_browse = None
        self.master = master
        self.master.title("Login")
        self.master.geometry("300x200")

        self.label_username = Label(master, text="Email:")
        self.label_username.pack(pady=5)
        self.entry_username = Entry(master)
        self.entry_username.pack(pady=5)

        self.label_password = Label(master, text="Password:")
        self.label_password.pack(pady=5)
        self.entry_password = Entry(master, show="*")
        self.entry_password.pack(pady=5)

        self.btn_login = Button(master, text="Login", command=self.validate_login)
        self.btn_login.pack(pady=10)

        self.btn_back = Button(master, text="Back", command=self.go_back)
        self.btn_back.pack(pady=5)

    def validate_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        try:
            from Auction import connect_to_db
            db = connect_to_db()

            cursor = db.cursor()
            cursor.callproc("get_user", [username, password])
            result = cursor.fetchone()
            if result:
                user = check_user_type(username, cursor)
                messagebox.showinfo("Login Successful", "Welcome, " + str(user[1]) + " " + str(user[3]) + "!")
                # Add your code to open the next page or perform actions after successful login
                if user[0] == "Seller":
                    self.goto_products(db, user[2])
                elif user[0] == "Bidder":
                    self.goto_bidder_options(db, user[2])

            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
                # Add your code for handling failed login attempts

        except pymysql.err.OperationalError:
            messagebox.showerror("Error connecting to the database: ")

    def go_back(self):
        self.master.destroy()
        self.master.quit()  # Quit the main loop

        import Auction
        Auction.ChooseOptionPage()

    def goto_bidder_options(self, db_connection, BidderID):
        self.master.destroy()
        self.master.quit()
        self.master = Tk()
        self.master.title("Options")
        self.master.geometry("400x300")

        self.btn_browse = Button(self.master, text="Browse", command=lambda: goto_browse(db_connection))
        self.btn_browse.pack(pady=5)

        self.btn_notifications = Button(self.master, text="Notifications",
                                        command=lambda: goto_notifications(db_connection, BidderID))
        self.btn_notifications.pack(pady=5)

        self.btn_purchases = Button(self.master, text="Your Purchases", command=lambda: self.show_purchases(db_connection, BidderID))
        self.btn_purchases.pack(pady=5)

        self.btn_logout = Button(self.master, text="Logout", command=self.go_back)
        self.btn_logout.pack(pady=5)

    def goto_products(self, db_connection, SellerID):
        self.master.destroy()
        self.master.quit()

        from Products import ProductsPage
        ProductsPage(db_connection, SellerID)

    def fetch_purchases_data(self,db_connection,  BidderID):
        cursor = db_connection.cursor()
        '''query = """
                        SELECT Item.Name, Bid.BidAmount
FROM Buys
INNER JOIN Item ON Buys.ItemID = Item.ItemID
INNER JOIN WinningBid ON Item.ItemID = WinningBid.ItemID
INNER JOIN Bid ON WinningBid.HighestBidID = Bid.BidID
WHERE Buys.BidderID = %s
                        """'''
        #ursor.execute(query, (BidderID,))
        cursor.callproc("get_purchase_data",[BidderID])
        purchases_data = cursor.fetchall()
        return purchases_data

    def show_purchases(self, db_connection, BidderID):
        purchases_data = self.fetch_purchases_data(db_connection, BidderID)
        if not purchases_data:
            # If purchases_data is empty, show a popup message
            messagebox.showinfo('No Purchases', 'You have not made any purchases yet.')
            return

        items = [item[0] for item in purchases_data]
        prices = [price[1] for price in purchases_data]

        # Create a pie chart
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(prices, labels=items, autopct='%1.1f%%')
        ax.set_title('Your Purchases')
        ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular

        # Embed the pie chart in a popup window
        popup = Toplevel(self.master)
        popup.title('Your Purchases')
        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Close button for the popup window
        close_btn = Button(popup, text='Close', command=popup.destroy)
        close_btn.pack()
