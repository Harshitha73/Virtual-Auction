import json
from tkinter import Tk, Button

import pymysql
from pymysql import cursors, connect

from LoginPage import LoginPage
from SignupPage import SignupPage

db_creds_path = "db_credentials.json"
with open(db_creds_path) as db_creds_file:
    db_creds = json.load(db_creds_file)
host = db_creds.get("host"),
charset = "utf8mb4",
cursor_class = cursors.DictCursor


def connect_to_db(user=db_creds.get("user"), password=db_creds.get("password"), database=db_creds.get("database")):
    try:
        conn = connect(host='localhost', user=user, password=password, db=database)
        return conn
    except pymysql.err.OperationalError:
        print("Error connecting to database")
        return None


class ChooseOptionPage:
    def __init__(self):
        self.master = Tk()
        self.master.title("Choose Login or Sign Up")
        self.master.geometry("300x150")

        self.btn_login = Button(self.master, text="Login", command=self.select_login)
        self.btn_login.pack(pady=10)

        self.btn_signup = Button(self.master, text="Sign Up", command=self.select_signup)
        self.btn_signup.pack(pady=10)

        self.master.mainloop()

    def select_login(self):
        self.master.destroy()
        LoginPage(Tk())

    def select_signup(self):
        self.master.destroy()
        SignupPage(Tk())


if __name__ == "__main__":
    choose_option = ChooseOptionPage()
    choose_option.master.mainloop()
