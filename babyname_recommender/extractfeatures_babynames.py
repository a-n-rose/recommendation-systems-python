import sqlite3
import numpy as np

class BuildTables:
    def __init__(self,database):
        self.database = database
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()
        
    def get_names(self): 
        msg = '''SELECT name_id, name FROM names '''
        self.c.execute(msg)
        names = self.c.fetchall()
        return names
    
    def create_feature_table(self):
        cols_types =[]
        letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        for letter in letters:
            cols_types.append("{} int".format(letter))
        cols_types.append("length int")
        cols_str = ','.join(cols_types)
        msg = '''CREATE TABLE IF NOT EXISTS basic_features(feature_name_id integer primary key, %s, FOREIGN KEY(feature_name_id) REFERENCES names(name_id) ) ''' % cols_str
        self.c.execute(msg)
        self.conn.commit()
        return None

    #def save_basic_features(self,prepped_data):
        #self.create_feature_table()
        #cols_var = []
        #for i in range(prepped_data.shape[1]):
            #cols_var.append(" ?")
        #cols = ",".join(cols_var)

        #msg = '''INSERT INTO basic_features_letters_length VALUES (%s) ''' % cols
        #self.c.executemany(msg,prepped_data)
        #self.conn.commit()
        #return None
    
    def create_default_clusters_table(self):
        msg = '''CREATE TABLE IF NOT EXISTS default_clusters(cluster_id INTEGER PRIMARY KEY, cluster INT, num_clusters INT, features_used TEXT, cluster_name_id INT, FOREIGN KEY(cluster_name_id) REFERENCES names(name_id)) '''
        self.c.execute(msg)
        self.conn.commit()
        return None
    
    def save_cluster_labels(self,prepped_cluster_data):
        '''
        How to organize the cluster labels? 
        '''
        msg = '''INSERT INTO default_clusters VALUES(NULL, ?, ?, ?, ?) '''
        self.c.executemany(msg,prepped_cluster_data)
        self.conn.commit()
        return None
    

    
class BuildFeatures:


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
    
    def define_features_letters_length(self,names):
        letters_int_dict, lengths_int_dict  = self.get_chars_length_dicts(names)
        num_cols = len(letters_int_dict)+1+1 #(1) length, 2) id )
        matrix_letters_length = self.coll_letter_length_data(names,num_cols)
        return matrix_letters_length
    
    def prep_defaultclusters_for_sql(self, name_list, cluster_list, num_clusters, features_used):
        prepped_clusters = []
        for i in range(len(name_list)):
            #append cluster assignment and name_id to list of tuples to save to sql table
            prepped_clusters.append((int(cluster_list[i]),num_clusters, features_used, name_list[i][0]))
        return prepped_clusters
        
        
