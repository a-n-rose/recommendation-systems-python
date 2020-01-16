'''
Class to create and handle IPA features

Note: SQLite has 2000 row limit
with the aded pair features, I had [5 rows x 2491 columns] (printed head of dataframe)

Removed columns with only False values --> [5 rows x 1177 columns] (printed head of dataframe)

Total duration to assign data to 30 clusters: 504.9951288700104 seconds, so appx 8 min (all names with all these features)

'''
import time
import sqlite3
import pandas as pd
import numpy as np
#from subprocess import check_output

#https://github.com/mphilli/English-to-IPA
import eng_to_ipa as ipa


import itertools
from ipa_chart_dicts import ipa_characters, ipa_vowels_dict, ipa_consonants_dict, ipa_stress_dict, ipa_vowels
from errors import IPAnotAligned

class IPA():
    def __init__(self,database):
        self.database = database
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()
        self.ipa_chars = ipa_characters()
        
    def get_names(self):
        start = time.time()
        msg = '''SELECT name_id, name, sex FROM names'''
        self.c.execute(msg)
        names = self.c.fetchall()
        print("{} sec".format(time.time()-start))
        return names
    
    def create_ipa_features_table(self):
        #create list with column name and data type
        cols_types = []
        
        for name in self.df_column_names:
            #some values, as in integers or "as" 
            #conflict with SQL; therefore, need ''
            #around column names
            cols_types.append("'{}' INT".format(name))

            
        # put list into string format for SQL statement
        cols_str = ','.join(cols_types)
        #print(cols_str)
        msg = '''CREATE TABLE IF NOT EXISTS features_ipa_extended(feature_name_id INTEGER PRIMARY KEY, %s, FOREIGN KEY(feature_name_id) REFERENCES names(name_id)) ''' % cols_str
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
        msg = '''INSERT INTO features_ipa_extended VALUES(%s) ''' % cols
        self.c.executemany(msg,ipa_data_SQL)
        self.conn.commit()
        return None
    
    def name_dict(self,names):
        start = time.time()
        #name_set[0] = name ID, name_set[1] = name
        name_dict = {}
        for name_id, name, sex in names:
            name_dict[name_id] = (name,sex)
        print("{} sec".format(time.time()-start))
        return name_dict
    
    def name2ipa(self,name_dict):
        '''
        espeak transcribes names into ipa_chars
        this takes a while
        '''
        start = time.time()
        name_df = pd.DataFrame.from_dict(name_dict,orient="index",columns=["name","sex"])
        name_df["ipa"] = name_df["name"].apply(lambda x: ipa.convert(x))
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
        print("adding features for each IPA character")
        
        name_ipa_df = self.apply_ipa_features(name_ipa_df)
        
        name_ipa_df = self.remove_nonunique_columns(name_ipa_df)
        
        self.set_final_df_column_names(name_ipa_df)
        print(name_ipa_df.columns)
        print("prepping features for sql")
        ipa_features_SQL = self.prep_ipa_features_SQL(name_ipa_df)
        #print("prepped features: {}".format(ipa_features_SQL[:20]))
        self.insert_ipa_features(ipa_features_SQL)
        return name_ipa_df.head(), self.df_column_names
    
    def prep_ipa_features_SQL(self,name_ipa_df):
        name_ipa_dict = name_ipa_df.to_dict(orient="index")
        datasql = []
        #key = name_id
        #value = dict of column names and values 
        for key, value in name_ipa_dict.items():
            vals = list(value.values())
            #start at index 1 to remove (redundant) name from feature table
            vals = vals[1:]
            #put in the name_id as first value
            vals.insert(0,key)
            datasql.append(tuple(vals))
        return datasql
    
    def remove_nonunique_columns(self,name_ipa_df):
        df_new = name_ipa_df.loc[:, (name_ipa_df != False).any(axis=0)]
        return df_new
    
    def collect_used_ipa(self,name_ipa_df):
        '''
        Collect all IPA chars used in the names dataset
        Collect the various lengths of IPA --> useful in features
        '''
        start = time.time()
        ipa_chars = []
        ipa_lengths = []
        for index, row in name_ipa_df.iterrows():
            ipa_chars.append(list(row[2]))
            ipa_len = len(row[2])
            if ipa_len not in ipa_lengths:
                ipa_lengths.append(ipa_len)
        #flatten the list and put it in order
        ipa_chars = sorted(set([item for sublist in ipa_chars for item in sublist]))
        #remove irrelevant characters: '/n'  ' ' 
        ipa_chars = [char for char in ipa_chars if char not in ["(",")","-","\n"," ","*"]]
        
        #to ensure the ipa characters are in the order I expect:
        try:
            if ipa_chars[-6] != ipa_stress_dict()["primary_stress"]:
                pass
                #raise IPAnotAligned("Collected IPA characters do not match expected values. {} does not equal {}".format(ipa_chars[-6],ipa_stress_dict()["primary_stress"]))
        except IndexError:
            raise IPAnotAligned("\nERROR!! \n\nHint:\nReview function 'collect_used_ipa()'. \nThe wrong column was likely used to collect ipa characters and name lengths.\n")
        print("{} sec".format(time.time()-start))
        return ipa_chars, ipa_lengths
    
    def apply_ipa_features(self,name_ipa_df):
        name_ipa_df = self.create_ipa_char_features(name_ipa_df)
        #name_ipa_df = self.create_ipa_pairs_features(name_ipa_df)
        print("adding length feature for the various lengths")
        
        name_ipa_df = self.create_length_features(name_ipa_df)
        print("adding stress features")
        name_ipa_df = self.create_stress_feature(name_ipa_df)
        print("adding phonetic features")
        name_ipa_df = self.create_phonetic_features(name_ipa_df)
        print("done")
        #print(name_ipa_df.head())
        return name_ipa_df
        
    
    def create_ipa_char_features(self,name_ipa_df):
        '''
        creates new column for each ipa character and fills in values for if name has the character or not
        '''
        start = time.time()
        #for char in self.ipa_chars:
            #name_ipa_df[char] = name_ipa_df['ipa'].apply(lambda x: char in x)
        
        
        ipa_pair_list = list(itertools.permutations(self.ipa_chars,2))
        ipa_pairs = []
        for ipa_pair in ipa_pair_list:
            ipa_pairs.append("".join(ipa_pair))
        for pair in ipa_pairs:
            name_ipa_df[pair] = name_ipa_df['ipa'].apply(lambda x: pair in x)
        
        print("{} sec".format(time.time()-start))
        return name_ipa_df
        
    def create_ipa_pairs_features(self,name_ipa_df):
        pass
    
    def create_length_features(self,name_ipa_df):
        start = time.time()
        #for length in self.ipa_lengths:
            #name_ipa_df[length] = name_ipa_df['ipa'].apply(lambda x: len(x) == length)
        name_ipa_df["short"] = name_ipa_df["ipa"].apply(lambda x: len(x) <= 6)
        name_ipa_df["mid"] = name_ipa_df["ipa"].apply(lambda x: len(x) > 6 and len(x) <= 11)
        name_ipa_df["long"] = name_ipa_df["ipa"].apply(lambda x: len(x) > 11 and len(x) <= 16)
        name_ipa_df["very_long"] = name_ipa_df["ipa"].apply(lambda x: len(x) > 16)
        print("{} sec".format(time.time()-start))
        return name_ipa_df
    
    def create_stress_feature(self,name_ipa_df):
        stress = ipa_stress_dict()
        name_ipa_df["trochee"] = name_ipa_df["ipa"].apply(lambda x: stress["primary_stress"] in x[:len(x)//2])
        #bug:  labels "Joan" as iambic... still quite helpful tho 
        name_ipa_df["iamb"] = name_ipa_df["ipa"].apply(lambda x: stress["primary_stress"] in x[len(x)//2:])
        
        name_ipa_df["secondary_stress"] = name_ipa_df["ipa"].apply(lambda x: stress["secondary_stress"] in x)
        
        name_ipa_df["long_vowel"] = name_ipa_df["ipa"].apply(lambda x: stress["long_vowel"] in x)
        
        return name_ipa_df
    
    def create_phonetic_features(self,name_ipa_df):
        
        #before name in ipa starts: ' ' space
        #skip it by indexing at 1
        try:
            name_ipa_df["start_with_vowel"] = name_ipa_df["ipa"].apply(lambda x: True if (len(x)>1 and x[0] in ipa_vowels() or x[1] in ipa_vowels()) else False)
        except IndexError:
            pass
        #after name in ipa ends:  '\n' 
        #skip it by indexing at -2
        try:
            name_ipa_df["end_with_vowel"] = name_ipa_df["ipa"].apply(lambda x: x[-1] in ipa_vowels())
        except IndexError:
            pass
        #vowel keys: open_vowels, mid_vowels, front_vowels, central_vowels, back_vowels, rounded_vowels
        for key, value in ipa_vowels_dict().items():
            #does the name have certain types of vowels in it
            name_ipa_df[key] = name_ipa_df["ipa"].apply(lambda x: True in [i in value for i in list(x) ] )
            
        #consonant keys: voiced, plosive, nasal, tril, tap, fricative, lateral_fricative, approximant, lateral_approximant, bilabial, labiodental, labiovelar, dental, alveolar, postalveolar, retroflex, palatal, velar, uvular, pharyngeal, glottal
        for key, value in ipa_consonants_dict().items():
            #does the name have certain types of vowels in it
            name_ipa_df[key] = name_ipa_df["ipa"].apply(lambda x: True in [i in value for i in list(x) ] )
        return name_ipa_df
    
    def set_final_df_column_names(self,name_ipa_df):
        #first column is name and we're not saving that in the database - have name_id for that
        cols = name_ipa_df.columns.values.tolist()[1:]
        self.df_column_names = cols
        print("Dataframe Columns: {}".format(cols))
        print("Num Cols: {}".format(len(cols)))
        return None
        
