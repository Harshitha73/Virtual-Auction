from tkinter import Label, Entry, Button, messagebox, OptionMenu, StringVar

import pymysql


class IncompleteInformationError(Exception):
    pass


class SignupPage:
    def __init__(self, master):
        self.master = master
        self.master.title("Sign Up")
        self.master.geometry("900x700")

        self.label_FirstName = Label(master, text="First Name:")
        self.label_FirstName.pack(pady=5)
        self.entry_FirstName = Entry(master)
        self.entry_FirstName.pack(pady=5)

        self.label_LastName = Label(master, text="Last Name:")
        self.label_LastName.pack(pady=5)
        self.entry_LastName = Entry(master)
        self.entry_LastName.pack(pady=5)

        self.label_Street = Label(master, text="Street:")
        self.label_Street.pack(pady=5)
        self.entry_Street = Entry(master)
        self.entry_Street.pack(pady=5)

        self.label_City = Label(master, text="City:")
        self.label_City.pack(pady=5)
        self.entry_City = Entry(master)
        self.entry_City.pack(pady=5)

        self.label_State = Label(master, text="State:")
        self.label_State.pack(pady=5)
        self.entry_State = Entry(master)
        self.entry_State.pack(pady=5)

        self.label_ZipCode = Label(master, text="Zip code:")
        self.label_ZipCode.pack(pady=5)
        self.entry_ZipCode = Entry(master)
        self.entry_ZipCode.pack(pady=5)

        self.label_PhoneNumber = Label(master, text="Phone number:")
        self.label_PhoneNumber.pack(pady=5)
        self.entry_PhoneNumber = Entry(master)
        self.entry_PhoneNumber.pack(pady=5)

        self.label_EmailID = Label(master, text="Email ID:")
        self.label_EmailID.pack(pady=5)
        self.entry_EmailID = Entry(master)
        self.entry_EmailID.pack(pady=5)

        self.label_Password = Label(master, text="Password:")
        self.label_Password.pack(pady=5)
        self.entry_Password = Entry(master, show="*")
        self.entry_Password.pack(pady=5)

        self.label_role = Label(master, text="Select Role:")
        self.label_role.pack(pady=5)

        # Options for the dropdown
        roles = ["Seller", "Bidder"]
        self.selected_role = StringVar(master)
        self.selected_role.set('')  # Setting an empty string as default

        # Dropdown to select the role
        self.role_dropdown = OptionMenu(master, self.selected_role, *roles)
        self.role_dropdown.pack(pady=5)

        self.btn_signup = Button(master, text="Sign Up", command=self.register_user)
        self.btn_signup.pack(pady=10)

        self.btn_back = Button(master, text="Back", command=self.go_back)
        self.btn_back.pack(pady=5)

    def check_email_existence(self, email, cursor):

        cursor.callproc("check_user_exists", [email])
        result = cursor.fetchone()

        if result:
            messagebox.showerror("Email ID already exists, please login!")
            self.go_back()

    def validate_input(self):
        # Get values from all Entry widgets
        values = [
            self.entry_FirstName.get(),
            self.entry_LastName.get(),
            self.entry_Street.get(),
            self.entry_City.get(),
            self.entry_State.get(),
            self.entry_ZipCode.get(),
            self.entry_PhoneNumber.get(),
            self.entry_EmailID.get(),
            self.entry_Password.get(),
            self.selected_role.get()
        ]

        # Check if any field is empty
        if '' in values:
            return False
        return True

    def register_user(self):

        try:
            if not self.validate_input():
                raise IncompleteInformationError("Please fill in all fields.")
            FirstName = self.entry_FirstName.get()
            LastName = self.entry_LastName.get()
            StreetAddress = self.entry_Street.get()
            City = self.entry_City.get()
            State = self.entry_State.get()
            ZipCode = int(self.entry_ZipCode.get())
            PhoneNumber = int(self.entry_PhoneNumber.get())
            EmailID = self.entry_EmailID.get()
            Password = self.entry_Password.get()
            selected_role = self.selected_role.get()
            from Auction import connect_to_db
            db = connect_to_db()
            cursor = db.cursor()
            self.check_email_existence(EmailID, cursor)
            if selected_role == "Seller":
                cursor.callproc("add_seller",
                                [FirstName, LastName, StreetAddress, City, State, ZipCode, PhoneNumber, EmailID,
                                 Password])

            elif selected_role == "Bidder":
                cursor.callproc("add_bidder",
                                [FirstName, LastName, StreetAddress, City, State, ZipCode, PhoneNumber, EmailID,
                                 Password])
            db.commit()

            messagebox.showinfo("Registration Successful",
                                "You are now registered, " + FirstName + " " + LastName + "!")
            self.go_back()  # After signup, proceed to login

        except pymysql.err.OperationalError:
            messagebox.showerror("Error connecting to the database: ")
        except ValueError:
            messagebox.showerror("Invalid Input", "Check the entered values correctly.")
        except IncompleteInformationError as e:
            messagebox.showerror("Incomplete Information", str(e))

    def go_back(self):
        self.master.destroy()
        self.master.quit()  # Quit the main loop

        import Auction
        Auction.ChooseOptionPage()
