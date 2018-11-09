import sqlite3
from errors import ExitApp
from random import shuffle

class BabynameRecommender:
    def __init__(self,database,user_id):
        self.database = database
        self.user_id = user_id
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()
        self.ratinglists = self.access_ratinglist_table()
        

    def access_ratinglist_table(self):
        msg = '''CREATE TABLE IF NOT EXISTS ratinglists(ratinglist_id integer primary key, ratinglist_name text, babyname_type int,ratinglist_order int, ratinglist_user_id int, FOREIGN KEY(ratinglist_user_id) REFERENCES users(user_id))'''
        self.c.execute(msg)
        self.conn.commit()
        return True

    def access_ratings_table(self):
        msg = '''CREATE TABLE IF NOT EXISTS ratings(rating_id integer primary key, rating int, rating_ratinglist_id int, rating_name_id int, FOREIGN KEY(rating_ratinglist_id) REFERENCES ratinglists(ratinglist_id), FOREIGN KEY(rating_name_id) REFERENCES names(name_id))'''
        self.c.execute(msg)
        self.conn.commit()
        return True
    
    def show_options_main(self):
        print("1) rate names\n2) search for names\n")
        return None
    
    def choose_options_main(self):
        choice = input()
        if choice.isdigit():
            return choice
        elif 'exit' in choice.lower():
            return None
        print("Please enter the corresponding digit or type 'exit'.")
        self.choose_options_main()
    
    def main_menu(self):
        self.show_options_main()
        choice = self.choose_options_main()
        if choice is None:
            raise ExitApp("User exited the program.")
        if 1 == int(choice):
            self.show_and_choose_lists()
            self.rate_names()
        elif 2 == int(choice):
            self.search_names()
        else:
            print("Please choose the corresponding digit.")
            self.main_menu()
        return None
    
    def make_list_dict(self,lists):
        list_dict = {}
        for i in range(len(lists)):
            list_dict[str(i+1)]=lists[i]
        self.list_dict = list_dict
        return None
    
    def show_lists(self,lists):
        for key, value in self.list_dict.items():
            print("{}) {}".format(key, value[1]))
        print("\nTo start a new name search, enter 'new': ")
        return None
    
    def get_list_choice(self):
        choice_list = input()
        return choice_list
    
    def get_lists(self):
        t = (self.user_id,)
        msg = '''SELECT * FROM ratinglists WHERE ratinglist_user_id=? '''
        self.c.execute(msg,t)
        lists = self.c.fetchall()
        return lists
    
    
    def select_list_from_choice(self,choice):
        for key, value in self.list_dict.items():
            if int(choice) == key:
                print(value)
                return value
        return None
        
    def show_and_choose_lists(self):
        lists = self.get_lists()
        if len(lists) > 0:
            self.make_list_dict(lists)
            self.show_lists(lists)
            list_choice = self.get_list_choice()
            if list_choice.isdigit():
                self.listchoice = list_choice
            elif 'new' in list_choice:
                self.create_new_ratinglist()
            elif 'exit' in list_choice:
                raise ExitApp("Couldn't choose a list?")
            else:
                print("Enter the corresponding number, 'new', or 'exit' to leave.")
                self.show_and_choose_lists()
        else:
            print("You don't have any name search lists yet.")
            self.create_new_ratinglist()
        return None
    
    def get_list_name(self):
        print("Enter the name for this recommender: ")
        name = input()
        return name
    
    def save_list(self,listname,babyname_type):
        lists = self.get_lists()
        list_order = str(len(lists)+1)
        self.listname = listname
        self.babyname_type = babyname_type
        t = (listname,babyname_type,list_order,self.user_id)
        msg = '''INSERT INTO ratinglists VALUES(NULL,?,?,?,?) '''
        self.c.execute(msg,t)
        self.conn.commit()
        return None
    
    def show_nametype_options(self):
        print("Name type:\n1) all names\n2) boy names\n3) girl names\n")
        return None
    
    def choose_babyname_type(self):
        choice = input()
        if choice.isdigit():
            if 1 == int(choice):
                babyname_type = choice
            elif 2 == int(choice):
                babyname_type = choice
            elif 3 == int(choice):
                babyname_type = choice
            else:
                print("Please enter the corresponding number.")
                self.choose_babyname_type()
        elif 'exit' in choice:
            raise ExitApp("Gender's no big deal!")
        else:
            print("Please enter the corresponding number or 'exit'.")
            self.choose_babyname_type()
        return babyname_type

    
    def set_mostrecentlist_as_listchoice(self):
        lists = self.get_lists()
        num_lists = len(lists)
        self.listchoice = num_lists
        return None
    
    def create_new_ratinglist(self):
        list_name = self.get_list_name()
        self.show_nametype_options()
        babyname_type = self.choose_babyname_type()
        self.save_list(list_name,babyname_type)
        lists_actualized = self.get_lists()
        self.make_list_dict(lists_actualized)
        self.set_mostrecentlist_as_listchoice()
        self.rate_names()
        return None
    
    def get_saved_babyname_type(self):
        t = (self.listchoice,self.user_id,)
        msg = '''SELECT babyname_type FROM ratinglists WHERE ratinglist_order=? AND ratinglist_user_id=? '''
        self.c.execute(msg,t)
        babyname_type = self.c.fetchall()
        return babyname_type[0][0]
    
    def get_names(self):
        babyname_type = self.get_saved_babyname_type()
        if int(babyname_type) == 1:
            msg = '''SELECT name_id, name FROM names'''
        elif int(babyname_type) == 2:
            msg = '''SELECT name_id, name FROM names WHERE sex='M' '''
        elif int(babyname_type) == 3:
            msg = '''SELECT name_id, name FROM names WHERE sex='F' '''
        else:
            raise ExitApp("Problem with babyname type.")
        self.c.execute(msg)
        names = self.c.fetchall()
        return names
    
    def rate_name(self,name):
        print("Enter 1 for 'like', 0 for 'dislike:")
        print("\n{}\n".format(name))
        rating = input()
        if rating.isdigit():
            if int(rating) == 0 or int(rating) ==1:
                return rating
        else:
            if 'exit' == rating.lower():
                return False
        
        return None
        

    def collect_name_ratings(self):
        collect = True
        self.access_ratings_table()
        names = self.get_names()
        shuffle(names)
        rating_dict = {}
        while collect == True:
            for i in range(len(names)):
                rating = self.rate_name(names[i][1])
                if rating == False:
                    collect = False
                    break
                elif rating.isdigit():
                    rating_dict[names[i][0]] = rating
        return rating_dict
                

    def get_list_id(self):
        t = (self.listchoice,self.user_id,)
        msg = '''SELECT ratinglist_id FROM ratinglists WHERE ratinglist_order=? AND ratinglist_user_id=? '''
        self.c.execute(msg,t)
        list_id = self.c.fetchall()
        if len(list_id) == 0:
            return None
        self.list_id = list_id[0]
        return list_id[0][0]
    
    def prep_rating_names_dict(self,rated_names_dict):
        list_id = self.get_list_id()
        prepped_list = []
        for key, value in rated_names_dict.items():
            prepped_list.append((int(value),list_id,key))
        return prepped_list
    
    def save_rated_names(self,prepped_list):
        msg = '''INSERT INTO ratings VALUES(NULL,?,?,?) '''
        self.c.executemany(msg,prepped_list)
        self.conn.commit()
        return None
    
    def rate_names(self):
        rated_names_dict = self.collect_name_ratings()
        print(rated_names_dict)
        prepped_list = self.prep_rating_names_dict(rated_names_dict)
        self.save_rated_names(prepped_list)
        return None
    
    def search_names(self):
        pass
            
