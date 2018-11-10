import sqlite3
import numpy as np
import pandas as pd

class LettersLength:
    def __init__(self,database):
        self.database = database
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()
        
    def get_names(self,babyname_sex=None): 
        self.babyname_type = babyname_sex
        if babyname_sex == 1:
            msg = '''SELECT name_id, name FROM names WHERE sex='M' '''
        elif babyname_sex == 2:
            msg = '''SELECT name_id, name FROM names WHERE sex='F' '''
        else:
            msg = '''SELECT name_id, name FROM names '''
        self.c.execute(msg)
        names = self.c.fetchall()
        return names
    
    def create_feature_table(self):
        cols_types =[]
        for key, value in self.letters_int_dict.items():
            cols_types.append("{} int".format(value))
        cols_types.append("length int")
        cols_str = ','.join(cols_types)
        msg = '''CREATE TABLE IF NOT EXISTS basic_features(feature_name_id integer primary key, %s, FOREIGN KEY(feature_name_id) REFERENCES names(name_id) ) ''' % cols_str
        self.c.execute(msg)
        self.conn.commit()
        return None
    
    def save_basic_features(self,prepped_data):
        cols_var = []
        for i in range(prepped_data.shape[1]):
            cols_var.append(" ?")
        cols = ",".join(cols_var)

        msg = '''INSERT INTO basic_features VALUES (%s) ''' % cols
        self.c.executemany(msg,prepped_data)
        self.conn.commit()
        return None

    def get_chars_length_dicts(self,names_tuple_list):
        letters_int_dict = {}
        letters_list = []
        length_int_dict = {}
        letter_count = 1
        length_count = 1
        for name_set in names_tuple_list:
            length = len(name_set[1])
            if str(length) not in length_int_dict:
                length_int_dict[str(length)] = length_count
                length_count+=1
            for letter in name_set[1]:
                if letter.lower() not in letters_list:
                    letters_list.append(letter.lower())
        alph_letters = sorted(letters_list)
        for i in range(len(alph_letters)):
            letters_int_dict[i+1] = alph_letters[i]
        self.letters_int_dict = letters_int_dict
        self.lengths_int_dict = length_int_dict
        return letters_int_dict, length_int_dict

    def coll_letter_length_data(self,names,num_columns):
        features_matrix = np.empty((len(names),num_columns))
      
        for i in range(len(names)):
            row = [names[i][0]]
            for j in range(len(self.letters_int_dict)):
                if self.letters_int_dict[j+1] in names[i][1].lower():
                    row.append(1)
                else:
                    row.append(0)
            row.append(len(names[i][1]))
            features_matrix[i] = row
        return features_matrix
    
    def define_features_letters_length(self,babyname_sex=None):
        names = self.get_names(babyname_sex)
        letters_int_dict, lengths_int_dict  = self.get_chars_length_dicts(names)
        print(self.lengths_int_dict)
        num_cols = len(letters_int_dict)+1+1 #(1) length, 2) id )
        matrix_letters_length = self.coll_letter_length_data(names,num_cols)
        self.create_feature_table()
        self.save_basic_features(matrix_letters_length)
        return None
