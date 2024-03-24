from tkinter import Toplevel, Button, Tk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class OptionsPage:
    def __init__(self, db, BidderID):
        self.btn_purchases = None
        self.btn_logout = None
        self.btn_notifications = None
        self.btn_browse = None
        self.db = db
        self.BidderID = BidderID
        self.master = Tk()
        self.master.title("Options")
        self.master.geometry("900x700")

    def show_options(self):
        self.btn_browse = Button(self.master, text="Browse", command=self.goto_browse)
        self.btn_browse.pack(pady=5)

        self.btn_notifications = Button(self.master, text="Notifications", command=self.goto_notifications)
        self.btn_notifications.pack(pady=5)

        self.btn_purchases = Button(self.master, text="Your Purchases", command=self.show_purchases)
        self.btn_purchases.pack(pady=5)

        self.btn_logout = Button(self.master, text="Logout", command=self.go_back)
        self.btn_logout.pack(pady=5)

    def fetch_purchases_data(self):
        cursor = self.db.cursor()
        query = """
                        SELECT Item.Name, Bid.BidAmount
FROM Buys
INNER JOIN Item ON Buys.ItemID = Item.ItemID
INNER JOIN WinningBid ON Item.ItemID = WinningBid.ItemID
INNER JOIN Bid ON WinningBid.HighestBidID = Bid.BidID
WHERE Buys.BidderID = %s
                        """
        cursor.execute(query, (self.BidderID,))
        purchases_data = cursor.fetchall()
        return purchases_data

    def show_purchases(self):
        purchases_data = self.fetch_purchases_data()
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

    def goto_browse(self):
        self.master.destroy()
        self.master.quit()
        from Browse import BrowsePage
        BrowsePage(self.db)

    def goto_notifications(self):
        self.master.withdraw()
        from Notifications import NotificationsPage
        # Create an instance of NotificationsPage with the database connection and BidderID
        notifications_page = NotificationsPage(self.db, self.BidderID, self.master)  # Pass the current master window
        notifications_page.show_notifications()

    def go_back(self):
        self.master.destroy()
        self.master.quit()
        import Auction
        Auction.ChooseOptionPage()
