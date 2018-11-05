import sqlite3
import numpy as np
import glob
import os

from errors import MissingNameID


class Setup_Name_DB:
    def __init__(self,database):
        self.database = database
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()
        
    def execute_commit_msg(self,msg,t=None):
        if t is None:
            self.c.execute(msg)
        else:
            self.c.execute(msg,t)
        self.conn.commit()
        return None

    def create_table_names(self):
        msg = '''CREATE TABLE IF NOT EXISTS names(name_id integer primary key, name text, sex text)  '''
        self.execute_commit_msg(msg)
        return None
    
    def create_table_popularity(self):
        #link year popularity table to names table
        msg = '''CREATE TABLE IF NOT EXISTS popularity(year_id integer primary key, year int, popularity int, year_name_id int, FOREIGN KEY(year_name_id) REFERENCES names(name_id) ) '''
        self.execute_commit_msg(msg)
        return None
    
    def check_if_name_exists(self,name,sex):
        msg = '''SELECT * FROM names WHERE name=? AND sex=? '''
        t = (name,sex,)
        self.c.execute(msg,t)
        names = self.c.fetchall()
        if len(names) == 0:
            return False
        else:
            return True
        
    def get_name_id(self,name,sex):
        t = (name,sex,)
        msg = '''SELECT name_id FROM names WHERE name=? AND sex=? '''
        self.c.execute(msg,t)
        name_id = self.c.fetchall()
        if len(name_id) == 1:
            return name_id[0][0]
        return None

    def collect_filenames(self):
        text_files = []
        for txt in glob.glob('./names/*.txt'):
            text_files.append(txt)
        text_files = sorted(text_files, reverse = False)
        return text_files
    
    def get_year(self,path2file):
        filename = os.path.splitext(path2file)[0]
        year = filename[-4:]
        return year
    
    def separate_name_data(self,data):
        name_data = [s.strip().split(',') for s in data.splitlines()]
        return name_data
    
    def get_name_info(self,name_entry):
        name = name_entry[0]
        sex = name_entry[1]
        popularity = name_entry[2]
        return name, sex, popularity
    
    def insert_name_data(self,data_entry,year):
        try:
            name,sex,popularity = self.get_name_info(data_entry)

            #insert name and sex data into names database
            # IF name doesn't exist
            name_exist = self.check_if_name_exists(name,sex)
            if name_exist == False:
                t = (name,sex,)
                msg = '''INSERT INTO names VALUES(NULL, ?, ?) '''
                self.execute_commit_msg(msg,t)
            else:
                print("name {} for sex {} exists already".format(name,sex))
            #insert name popularity into years database:
            msg = '''INSERT INTO popularity VALUES(NULL, ?, ?, ?) '''
            name_id = self.get_name_id(name,sex)
            if name_id is None:
                raise MissingNameID("The name ID for the name {} for sex {} cannot be collected".format(name,sex))
            t = (str(year),str(popularity),str(name_id),)
            self.execute_commit_msg(msg,t)
        except MissingNameID as e:
            print(e)
            pass
        finally:
            self.conn.commit()
        return None
    
    def save_name_data_2_SQL(self):
        #collect filenames
        text_files = self.collect_filenames()
        num_years = len(text_files)
        count_years = 0
        # I did a for loop here to reduce memory costs.
        for text_path in text_files:
            with open(text_path) as f:
                data = f.read()
            year = self.get_year(text_path)
            print("Processing names in the year {}".format(year))
            name_data =  self.separate_name_data(data)
            num_names = len(name_data)
            count_names = 0
            for entry in name_data:
                self.insert_name_data(entry,year)
                count_names+=1
                section = 'names of {}'.format(year)
                self.progress(count_names,num_names,section)
            count_years += 1
            self.progress(count_years,num_years,'all years')
        return None
    
    def progress(self,curr_count,total_count,section):
        percent = round(curr_count/float(total_count)*100,2)
        print("{}% through {}".format(percent,section))
        return None
    
