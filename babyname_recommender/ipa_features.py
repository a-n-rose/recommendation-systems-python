'''
Class to create and handle IPA features
'''
import time
import sqlite3
import pandas as pd
import numpy as np
from subprocess import check_output

class IPA():
    def __init__(self,database):
        self.database = database
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()
        
    def get_names(self):
        start = time.time()
        msg = '''SELECT name_id, name FROM names '''
        self.c.execute(msg)
        names = self.c.fetchall()
        print("{} sec".format(time.time()-start))
        return names
    
    def create_ipa_features_table(self):
        #create list with column name and data type
        cols_types = []
        chars = self.ipa_chars
        lens = self.ipa_lengths
        for char in chars:
            cols_types.append("{} INT".format(char))
        for length in lens:
            cols_types.append("'{}' INT".format(length))
            
        # put list into string format for SQL statement
        cols_str = ','.join(cols_types)
        msg = '''CREATE TABLE IF NOT EXISTS basic_features_ipa_chars_length(feature_name_id INTEGER PRIMARY KEY, ipa TEXT, %s, FOREIGN KEY(feature_name_id) REFERENCES names(name_id)) ''' % cols_str
        self.c.execute(msg)
        self.conn.commit()
        return None
    
    def insert_ipa_features(self,ipa_data_SQL):
        '''
        ipa_data_SQL is a list of tuples
        each tuple contains data in correct order
        '''
        self.create_ipa_features_table()
        #create the correct number of '?' for SQL insert statement
        cols_var = []
        for i in range(len(ipa_data_SQL[0])):
            cols_var.append(" ?")
        #prepare it into a string for statement
        cols = ",".join(cols_var)
        msg = '''INSERT INTO basic_features_ipa_chars_length VALUES(%s) ''' % cols
        self.c.executemany(msg,ipa_data_SQL)
        self.conn.commit()
        return None
    
    def name_dict(self,names):
        start = time.time()
        #name_set[0] = name ID, name_set[1] = name
        name_dict = {}
        for name_id, name in names:
            name_dict[name_id] = name
        print("{} sec".format(time.time()-start))
        return name_dict
    
    def name2ipa(self,name_dict):
        '''
        espeak transcribes names into ipa_chars
        this takes a while
        '''
        start = time.time()
        name_df = pd.DataFrame.from_dict(name_dict,orient="index",columns=["name"])
        name_df["ipa"] = name_df["name"].apply(lambda x: check_output(["espeak","-q","--ipa","-v","en-us",x]).decode("utf-8"))
        print("{} hours".format((time.time()-start)/3600.))
        return name_df
    
    def create_ipa_features(self):
        print("collecting names")
        names = self.get_names()
        print("creating name dictionary to store name and name id values")
        name_dict = self.name_dict(names)
        print("creating dataframe to store IPA features - transcribing names into IPA")
        name_ipa_df = self.name2ipa(name_dict)
        print("collecting all IPA characters used")
        self.ipa_chars, self.ipa_lengths = self.collect_used_ipa(name_ipa_df)
        print(self.ipa_chars)
        print("adding a feature for each IPA character")
        name_ipa_df = self.create_ipa_char_features(name_ipa_df)
        print("adding length feature for the various lengths")
        name_ipa_df = self.create_length_features(name_ipa_df)
        ipa_features_SQL = self.prep_ipa_features_SQL(name_ipa_df)
        self.insert_ipa_features(ipa_features_SQL)
        return ipa_features_SQL
    
    def prep_ipa_features_SQL(self,name_ipa_df):
        name_ipa_dict = name_ipa_df.to_dict(orient="index")
        datasql = []
        #key = name_id
        #value = dict of column names and values 
        for key, value in name_ipa_dict.items():
            vals = list(value.values())
            #start at index 1 to remove name and ipa transcription from feature table
            vals = vals[1:]
            vals.insert(0,key)
            datasql.append(tuple(vals))
        return datasql
    
    def collect_used_ipa(self,name_ipa_df):
        '''
        Collect all IPA chars used in the names dataset
        Collect the various lengths of IPA --> useful in features
        '''
        start = time.time()
        ipa_chars = []
        ipa_lengths = []
        for index, row in name_ipa_df.iterrows():
            ipa_chars.append(list(row[1]))
            ipa_len = len(row[1])
            if ipa_len not in ipa_lengths:
                ipa_lengths.append(ipa_len)
        #flatten the list and put it in order
        ipa_chars = sorted(set([item for sublist in ipa_chars for item in sublist]))
        #remove irrelevant characters: '/n'  ' ' 
        ipa_chars = [char for char in ipa_chars if char not in ["(",")","-","\n"," "]]
        print("primary stress = {}".format(ipa_chars[-6]))
        print("A as in Apple is {}".format(ipa_chars[22]))
        print("{} sec".format(time.time()-start))
        return ipa_chars, ipa_lengths
    
    def create_ipa_char_features(self,name_ipa_df):
        '''
        creates new column for each ipa character and fills in values for if name has the character or not
        '''
        start = time.time()
        for char in self.ipa_chars:
            name_ipa_df[char] = name_ipa_df['ipa'].apply(lambda x: char in x)
        print("{} sec".format(time.time()-start))
        return name_ipa_df
    
    def create_length_features(self,name_ipa_df):
        start = time.time()
        for length in self.ipa_lengths:
            name_ipa_df[length] = name_ipa_df['ipa'].apply(lambda x: len(x) == length)
        print("{} sec".format(time.time()-start))
        return name_ipa_df
    
    def create_trochee_feature(self):
        pass
        
   
## IPA CHARACTERS 

#ipa_chars = ['a', 'b', 'd', 'e', 'f', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'z', 'æ', 'ð', 'ø', 'ŋ', 'ɐ', 'ɑ', 'ɔ', 'ə', 'ɚ', 'ɛ', 'ɜ', 'ɡ', 'ɣ', 'ɪ', 'ɬ', 'ɹ', 'ɾ', 'ʃ', 'ʊ', 'ʌ', 'ʒ', 'ʔ', 'ˈ', 'ˌ', 'ː', '̩', 'θ', 'ᵻ']
#prim_stress = ipa_chars[-6]
#sec_stress = ipa_chars[-5]
#long_vowel = ipa_chars[-4]
#english button = ipa_chars[-3] #like in Hel*en*, butt*on*, Mount*ain*, it goes under the n




    
        
    
    

            
