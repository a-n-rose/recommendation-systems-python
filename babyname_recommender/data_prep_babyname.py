import sqlite3
import numpy as np
import glob
import os
import time
from sqlite3 import Error


class Setup_Name_DB:
    def __init__(self,database):
        self.database = database
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()
        
    def execute_commit_msg(self,msg,t=None,many=False):
        if t is None:
            self.c.execute(msg)
        else:
            if many == False:
                self.c.execute(msg,t)
            else:
                self.c.executemany(msg,t)
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
    
    def organize_name_data(self,year_data_dict):
        
        #need ids when inserting batch data into SQL tables
        #create them by using count_years and count_names
        name_sex_ids = {}
        year_popularity_ids = {}
        
        count_years = 1 
        count_names = 1
        for key,value in year_data_dict.items():
            year = key
            
            for entry in value:
                name,sex,popularity = self.get_name_info(entry)
                if (name,sex) not in name_sex_ids:
                    name_sex_ids[(name,sex)]=count_names
                    count_names+=1
                year_popularity_ids[(year,popularity,name_sex_ids[(name,sex)])] = count_years
                count_years += 1
        return name_sex_ids, year_popularity_ids
    
    def data_2_dict(self):
        #collect filenames
        text_files = self.collect_filenames()
        num_years = len(text_files)
        count_years = 0
        year_data_dict = {}
        for text_path in text_files:
            year_start = time.time()
            with open(text_path) as f:
                data = f.read()
            year = self.get_year(text_path)
            print("Processing names in the year {}".format(year))
            name_data =  self.separate_name_data(data)
            year_data_dict[year] = name_data
        return year_data_dict
    
    def prep_dict_4_SQL(self,names_dict,years_dict):
        names_prepped = []
        years_prepped = []
        for key, value in names_dict.items():
            names_prepped.append((value,key[0],key[1]))
        for key, value in years_dict.items():
            years_prepped.append((value,key[0],key[1],key[2]))
        return names_prepped, years_prepped
    
    def batch_insert_data(self,names_prepped,years_prepped):
        try:
            msg_names = '''INSERT INTO names VALUES(?,?,?) '''
            msg_years = '''INSERT INTO popularity VALUES(?,?,?,?) '''
            self.execute_commit_msg(msg_names,names_prepped,many=True)
            self.execute_commit_msg(msg_years,years_prepped,many=True)
            return True
        except Error as e:
            print("Database Error occured: {}".format(e))
        finally:
            self.conn.close()
        return None
    
    def collect_save_data(self):
        data_dict = self.data_2_dict()
        name_data_dict, year_data_dict = self.organize_name_data(data_dict)
        names4sql, years4sql = self.prep_dict_4_SQL(name_data_dict,year_data_dict)
        success = self.batch_insert_data(names4sql,years4sql)
        return success
