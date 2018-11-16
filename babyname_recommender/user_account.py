import sqlite3        
import re
from errors import ExitApp
from input_manager import rem_space_specialchar

class LoginUser:
    def __init__(self,database):
        self.database = database
        self.conn = sqlite3.connect(self.database)
        self.c = self.conn.cursor()

# Set up the user's account: logging in or registering

    def get_username(self):
        print("\nUsername: ")
        username = input("Spaces and special characters will be removed: ")
        username = rem_space_specialchar(username)
        if 'exit' == username.lower():
            raise ExitApp("Aw man. I didn't even catch your name. Come back soon!") 
        if username:
            return username
        else:
            print("Not enough alphanumeric characters used. Try again.")
            self.get_username()
        return None
    
    def get_password(self):
        print("\nPassword: ")
        password = input()
        return password
    
    def login(self,username):
        print("\nEnter your password to access your lists.\n")
        password = self.get_password()
        if 'exit' == password.lower():
            raise ExitApp("Aw man. You're leaving already? Come back soon!") 
        if password:
            match = self.check_password(username, password)
            return match
        return None
        
    def register(self,username):
        print("\nWelcome {}! Enter a password to create your account".format(username))
        password = self.get_password()
        if password:
            self.add_user(username,password)
            return True
        else:
            return False

    def sign_in(self):
        username = self.get_username()
        exist, user_id = self.check_if_user_exists(username)
        if exist == False:
            print("\nYour username will be saved as '{}'".format(username))
            logged_in = self.register(username)
        else:
            print("\nWelcome back {}! \n".format(username))
            logged_in = self.login(username)
            if logged_in == False:
                print("Either the password is incorrect or the username is taken. Please try again.")
                self.sign_in()
        return None
        
    def access_users_table(self):
        msg = '''CREATE TABLE IF NOT EXISTS users(user_id integer primary key, username text, password text)'''
        self.c.execute(msg)
        self.conn.commit()
        return None
    
    def check_if_user_exists(self,username):
        self.access_users_table()
        t = (username,)
        self.c.execute('''SELECT * FROM users WHERE username=? ''', t)
        users = self.c.fetchall()
        if len(users) == 1:
            return True, users[0][0]
        elif len(users) == 0:
            return False, None
        return None, None
    
    def check_password(self,username, password):
        t = (username,)
        msg = '''SELECT password FROM users WHERE username=? ''' 
        self.c.execute(msg,t)
        real_password = self.c.fetchall()[0][0]
        if password == real_password:
            self.is_user = True
            self.username = username
            _, self.user_id = self.check_if_user_exists(username)
            return True
        else:
            self.is_user = False
        return False
        
    def add_user(self,username,password):
        self.username = username
        t = (username,password,)
        msg = '''INSERT INTO users VALUES (NULL,?,?) '''
        self.c.execute(msg,t)
        self.conn.commit()
        self.is_user, self.user_id = self.check_if_user_exists(username)
        print("\nYou're account has been created.\nGet started by creating your first list.\n")
        
        return None
    
    def get_userid(self,username):
        t = (self.username,)
        msg = '''SELECT user_id FROM users WHERE username=? '''
        self.c.execute(msg,t)
        userid = self.c.fetchall()[0]
        if len(userid) == 1:
            return userid[0]
        return None
    
    def close(self):
        if self.conn:
            self.conn.close()
        return None
