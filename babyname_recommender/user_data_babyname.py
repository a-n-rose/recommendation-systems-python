'''
Recommender for names based off of International Phonetic Alphabet and Phonetic Classifications

Some areas "need improvement" - search word to find where

Uses SKlearn KMeans clustering and reverse feature selection (RFE) individualize cluster assignments to user's likes and dislikes

Users can create multiple searches, search all names, boy names only or girl names only. The user can save names they get recommended.

Can alter the number of features to select when creating clusters: fewer features result in more specific and simplified recommendations and more features result in a lot more variety.

ORGANIZATION:
functions below are loosely organized by the following:

1) SQL functions
2) main functions (e.g. main menu, rate names, recommend names, see saved names)
3) sub functions - functions that are called within main functions

'''


import pandas as pd
import numpy as np
import sqlite3
import time
from errors import ExitApp, ExitFunction, RatingsOnlyOneKind
from random import shuffle
from build_clusters import BuildClusters
from columns_ipa_extended import get_rel_features

class UserData:
    def __init__(self,database,user_id,num_clusters=None,num_features = None):
        self.database = database
        self.user_id = user_id
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()
        self.access_ratinglist_table()
        if num_clusters is None:
            self.num_clusters = 30
        else:
            self.num_clusters = num_clusters
        self.features_used = "features_ipa_extended"
        if num_features == None:
            self.num_features = 10
        else:
            self.num_features = num_features
        
####################### SQL FUNCTIONS #########################################

# CREATE/INITIATE TABLES

    def access_ratinglist_table(self):
        msg = '''CREATE TABLE IF NOT EXISTS users_ratinglists(ratinglist_id INTEGER PRIMARY KEY, ratinglist_name TEXT, babyname_type INT,ratinglist_order INT, version INT, ratinglist_user_id INT, FOREIGN KEY(ratinglist_user_id) REFERENCES users(user_id))'''
        self.c.execute(msg)
        self.conn.commit()
        return None
    

    def access_ratings_table(self):
        msg = '''CREATE TABLE IF NOT EXISTS ratings(rating_id integer primary key, rating int, rating_ratinglist_id int, rating_name_id int, FOREIGN KEY(rating_ratinglist_id) REFERENCES users_ratinglists(ratinglist_id), FOREIGN KEY(rating_name_id) REFERENCES names(name_id))'''
        self.c.execute(msg)
        self.conn.commit()
        return None
    
    def access_user_clusters_table(self):
        msg = '''CREATE TABLE IF NOT EXISTS users_clusters_updates(cluster_id INTEGER PRIMARY KEY, cluster INT, num_clusters INT, features_used TEXT, list_version INT, cluster_name_id INT, cluster_ratinglist_id INT, FOREIGN KEY(cluster_name_id) REFERENCES names(name_id), FOREIGN KEY(cluster_ratinglist_id) REFERENCES users_ratinglists(ratinglist_id)) ''' 
        self.c.execute(msg)
        self.conn.commit()
        return None
        
    def access_saved_names_table(self):
        msg = '''CREATE TABLE IF NOT EXISTS users_saved_names(saved_name_id INTEGER PRIMARY KEY, name TEXT, list_id INT, FOREIGN KEY(list_id) REFERENCES users_ratinglists(ratinglist_id)) '''
        self.c.execute(msg)
        self.conn.commit()
        return None

# INSERT STATEMENTS
    
    def update_clusters_database(self,new_clusters_prepped):
        
        msg = '''INSERT INTO users_clusters_updates VALUES(NULL,?, ?, ?, ?, ?, ?) '''
        self.c.executemany(msg,new_clusters_prepped)
        self.conn.commit()
        return None
    
    def save_list(self,listname,babyname_type):
        lists = self.get_lists()
        list_order = str(len(lists)+1)
        self.listname = listname
        self.babyname_type = babyname_type
        t = (listname,babyname_type,list_order,self.list_version,self.user_id)
        msg = '''INSERT INTO users_ratinglists VALUES(NULL,?,?,?,?,?) '''
        self.c.execute(msg,t)
        self.conn.commit()
        return None
    
    def save_rated_names(self,prepped_list):
        msg = '''INSERT INTO ratings VALUES(NULL,?,?,?) '''
        self.c.executemany(msg,prepped_list)
        self.conn.commit()
        return None
    
    def get_list_version(self):
        msg = '''SELECT version FROM users_ratinglists WHERE ratinglist_id=?  '''
        t = (self.list_id,)
        self.c.execute(msg,t)
        list_version = self.c.fetchall()[0][0]
        self.list_version = list_version
        return list_version
    
    def list_update(self):
        prev_version = self.get_list_version()
        print("previous version: {}".format(prev_version))
        curr_version = int(prev_version) + 1
        print("current version: {}".format(curr_version))
        msg = '''UPDATE users_ratinglists SET version=? WHERE ratinglist_id=? ''' 
        t = (curr_version,self.list_id)
        self.c.execute(msg,t)
        self.conn.commit()
        return None
    
    def insert_saved_names(self, prepped_saved_names):
        msg = '''INSERT INTO users_saved_names VALUES(NULL, ?, ?) '''
        self.c.executemany(msg,prepped_saved_names)
        self.conn.commit()
        return None
    
# SELECT STATEMENTS ( 1) lists, 2) clusters, 3) names )
    
    def get_lists(self):
        t = (self.user_id,)
        msg = '''SELECT * FROM users_ratinglists WHERE ratinglist_user_id=? '''
        self.c.execute(msg,t)
        lists = self.c.fetchall()
        return lists
    
    def get_list_id(self):
        t = (self.listchoice,self.user_id,)
        msg = '''SELECT ratinglist_id FROM users_ratinglists WHERE ratinglist_order=? AND ratinglist_user_id=? '''
        self.c.execute(msg,t)
        list_id = self.c.fetchall()
        if len(list_id) == 0:
            return None
        self.list_id = list_id[0][0]
        return list_id[0][0]
    
    def check_for_clusters(self):
        self.access_user_clusters_table()
        t = (self.get_list_id(),self.num_clusters,self.features_used,self.get_list_version())
        #leaving the WHERE specifications if other features used
        msg = '''SELECT cluster FROM users_clusters_updates WHERE cluster_ratinglist_id=? AND num_clusters=? AND features_used=? AND list_version=? LIMIT 10 '''
        self.c.execute(msg,t)
        clusters = self.c.fetchall()
        if len(clusters) == 10:
            return True
        else:
            return False
        return None
    
    def get_clusters_nameid(self):
        t = (str(self.list_id),str(self.num_clusters),self.features_used,self.list_version)
        msg = '''SELECT cluster_name_id, cluster FROM users_clusters_updates WHERE cluster_ratinglist_id=? AND num_clusters=? AND features_used=? AND list_version=?'''
        self.c.execute(msg,t)
        name_clusters = self.c.fetchall()
        return name_clusters

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

    def get_saved_babyname_type(self):
        '''
        The assigned sex of the babynames used: 1 = all, 2 = boy, 3 = girl
        '''
        t = (self.listchoice,self.user_id,)
        msg = '''SELECT babyname_type FROM users_ratinglists WHERE ratinglist_order=? AND ratinglist_user_id=? '''
        self.c.execute(msg,t)
        babyname_type = self.c.fetchall()
        return babyname_type[0][0]
    
    def get_rated_names(self):
        t = (self.list_id,)
        msg = '''SELECT rating_name_id,rating FROM ratings WHERE rating_ratinglist_id=? '''
        self.c.execute(msg,t)
        ratings = self.c.fetchall()
        return ratings
    
    def get_names_nameids(self):
        msg = '''SELECT name, name_id FROM names '''
        self.c.execute(msg)
        names = self.c.fetchall()
        return names
    
    def get_extended_ipa_name_features(self):
        #used * because columns span the alphabet.. don't want to write that all down here...
        babyname_type = self.get_saved_babyname_type()
        if int(babyname_type) == 1:
            msg = '''SELECT * FROM features_ipa_extended'''
        elif int(babyname_type) == 2:
            msg = '''SELECT * FROM features_ipa_extended WHERE sex='M' '''
        elif int(babyname_type) == 3:
            msg = '''SELECT * FROM features_ipa_extended WHERE sex='F' '''
        self.c.execute(msg)
        extended_features = self.c.fetchall()
        return extended_features
        
    def get_saved_names(self):
        msg = '''SELECT name FROM users_saved_names WHERE list_id=? '''
        t = (self.list_id,)
        self.c.execute(msg,t)
        saved_names = self.c.fetchall()
        return saved_names

####################### MAIN FUNCTIONS THAT CALL OTHER FUNCTIONS #########################################
    
    def main_menu(self):
        print("\nMAIN MENU\n")
        self.show_options_main()
        choice = self.choose_options_main()
        if choice is None:
            raise ExitApp("User exited the program.")
        if 1 == int(choice):
            #choice to rate names
            self.show_and_choose_lists()
            self.rate_names() 
        elif 2 == int(choice):
            #choice to get recommendations and save names
            self.show_and_choose_lists()
            self.activate_clusters()
            self.recommend_names()
        elif 3 == int(choice):
            #choice to see your saved names
            self.show_and_choose_lists()
            self.show_saved_names()
            self.main_menu()
        else:
            print("Please choose the corresponding digit.")
            self.main_menu()
        return None
        
        
    def rate_names(self):
        rated_names_dict = self.collect_name_ratings()
        prepped_list = self.prep_rating_names_dict(rated_names_dict)
        self.save_rated_names(prepped_list)
        updated = self.update_clusters()
        if updated:
            print("clusters updated!")
            self.list_update()
            print("list version updated")
        self.main_menu()
        return None

    def recommend_names(self):
        #create dictionary containing the current clusters assigned to each name (according to the search list)
        nameid_cluster_dict = self.get_cluster_name_dict()
        
        #collect the ratings the user has made so far (according to the search list)
        ratings = self.get_rated_names()
        
        #separate liked from disliked names - see how well the clusters are separating these
        liked_name_ids = self.sort_rated_names(ratings)
        liked_clusters = self.get_assigned_clusters(liked_name_ids,nameid_cluster_dict)
        
        #build recommendations based on cluster numbers --> recommend names with same cluster number as liked names
        #this *needs improvement*
        rec_name_ids = self.get_recommended_name_ids(liked_clusters,nameid_cluster_dict)
        name_id_tuple = self.get_names_nameids()
        name_id_dict = self.get_name_nameid_dict(name_id_tuple)
        rec_names = self.nameid_to_name(rec_name_ids,name_id_dict)
        
        #Present recommended names one by one
        #user can rate the name to see how well the recommender worked
        #user can save names they like
        rec_ratings_dict, users_saved_names = self.collect_recommendation_ratings(rec_names)
        self.insert_saved_names(users_saved_names)
        bc = BuildClusters()
        recommendation_score = bc.accuracy_recommendations(rec_ratings_dict)
        print("This recommender found names you liked {}%  of the time".format(recommendation_score))
        print("\nRecommender built with feature type: {}\n Number of selected features: {}\n".format(self.features_used,self.num_features))
        self.main_menu()
        
        return None
     
    def show_saved_names(self):
        self.access_saved_names_table()
        saved_names = self.get_saved_names()
        if len(saved_names) == 0:
            print("You haven't saved any names yet.\n")
        else:
            print("YOUR SAVED NAMES:\n\n")
            for name in saved_names:
                print(name[0])
            print("\n\n")
        return None
        
            
####################### SUPPORT FUNCTIONS CALLED BY MAIN FUNCTIONS ########################################################################################################################################################################################################################################################################################################################################




#############################################################################
# def main menu
#############################################################################

    def show_options_main(self):
        print("1) rate names\n2) see recommendations\n3) see your saved names")
        return None
    
    def choose_options_main(self):
        choice = input()
        if choice.isdigit():
            return choice
        elif 'exit' in choice.lower():
            return None
        print("Please enter the corresponding digit or type 'exit'.")
        self.choose_options_main()

    def show_and_choose_lists(self):
        '''
        Shows the lists the user made so far. If the user wants to 
        create a new one, type in 'new'. If there aren't any lists,
        the user is prompted to create one.
        '''
        lists = self.get_lists()
        if len(lists) > 0:
            self.make_list_dict(lists)
            self.show_lists(lists)
            listchoice = self.get_listchoice()
            if listchoice.isdigit():
                self.listchoice = listchoice
                self.list_id = self.get_list_id()
                self.list_version = self.get_list_version()
            elif 'new' in listchoice:
                self.create_new_ratinglist()
            elif 'exit' in listchoice:
                raise ExitApp("Couldn't choose a list?")
            else:
                print("Enter the corresponding number, 'new', or 'exit' to leave.")
                self.show_and_choose_lists()
        else:
            print("You don't have any name search lists yet.")
            self.create_new_ratinglist()
        return None

    def activate_clusters(self):
        self.access_user_clusters_table()
        #check if clusters exist 
        clusters_exist = self.check_for_clusters()
        if clusters_exist is False:
            print("Please rate some names first.")
            self.main_menu()
        return None
        
# def show_and_choose_lists

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
    
    def get_listchoice(self):
        choice_list = input()
        return choice_list

# create_new_ratinglist

    def get_list_name(self):
        print("Enter the name for this recommender: ")
        name = input()
        return name

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
        '''
        Set important variables for identifying names related to this list.
        i.e. babyname_type (all names, boy names, girl names)
        self.listchoice --> useful in getting list_id later in program
        '''
        self.list_version = 1
        list_name = self.get_list_name()
        self.show_nametype_options()
        babyname_type = self.choose_babyname_type()
        self.save_list(list_name,babyname_type)
        lists_actualized = self.get_lists()
        self.make_list_dict(lists_actualized)
        self.set_mostrecentlist_as_listchoice()
        self.access_user_clusters_table()
        self.activate_clusters()
        self.rate_names()
        return None
    
    
#############################################################################
# rate names
#############################################################################

    def rate_name(self,name):
        print("\nEnter 1 for 'like', 0 for 'dislike:")
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
        names_rated = 0
        self.access_ratings_table()
        names = self.get_names()
        shuffle(names)
        rating_dict = {}
        while collect == True:
            for i in range(len(names)):
                if collect == False:
                    break
                rating = self.rate_name(names[i][1])
                if rating == False:
                    collect = False
                    break
                elif rating is None:
                    pass
                elif rating.isdigit():
                    names_rated+=1
                    rating_dict[names[i][0]] = rating
                if names_rated == 25:
                    print("25 names rated")
                elif names_rated == 50:
                    print("50 names rated")
        return rating_dict
    
    def prep_rating_names_dict(self,rated_names_dict):
        list_id = self.get_list_id()
        prepped_list = []
        #key = name_id, value = rating
        for key, value in rated_names_dict.items():
            prepped_list.append((int(value),list_id,key))
        return prepped_list
    

    
    def update_clusters(self):
        '''
        After rating names, the clusters will be updated
        For now this is a bit slow and should be made more efficient
        *needs improvement* 
        
        First, see which features are the most useful in predicting 
        whether the user likes a name or not. Reduce number of features 
        to only those (specified in number in self.num_features)
        
        Then, apply those features to cluster generation for all names.
        Also, apply weights to the names rated positively
        '''
        
        start = time.time()
        bc = BuildClusters()
        
        try:
            ################################################################
            #Step 1
            
            #collected rated names and features --> dict --> dataframe --> RFE()
            all_rated_names = self.get_rated_names()
            name_features = self.get_extended_ipa_name_features()
            name_features_dict = bc.features_2_dict(name_features)
            ratednames_features_dict = bc.ratednames_features_2_dict(name_features_dict,all_rated_names)
            
            #dataframe to more easily organize data
            #weights are the name_ids that the user liked
            rated_names_df, weights_liked_nameids = bc.dict2dataframe(ratednames_features_dict,ratings=True)
            
            #prep the values for reverse feature selection:
            #features
            rated_names_features_df = rated_names_df.iloc[:,:-1]
            #ratings/labels
            rated_names_ratings_df = rated_names_df.iloc[:,-1]
            
            #note, since my features are already one-hot-encoded, don't need to one-hot-encode
            encoded_feature_cols = rated_names_features_df.columns
            feature_matrix_reduced, labels_chosen = bc.prune_features(rated_names_features_df.values,rated_names_ratings_df.values,self.num_features)
            if labels_chosen is not None:
                selected_feature_indices = np.where(labels_chosen)
            else:
                raise RatingsOnlyOneKind()
        
            ##############################################################
            #Step 2
            
            #Now update clusters for ALL names, based on the selected features
            #of the names the user rated
            #get names and features to dict --> dataframe --> KMeans clustering
            
            
            #name_weights are the weights that will be put into the KMeans clustering algorithm
            all_names_df, all_name_ids = bc.dict2dataframe(name_features_dict,weight_name_ids=weights_liked_nameids)
            #features
            all_names_df = all_names_df.iloc[:,:-1]
            #weights
            all_names_weights = all_names_df.iloc[:,-1]
            
            #ensure rating is not included, datframe should only have column len of 1176
            if len(all_names_df.columns) > 1176:
                all_names_df = all_names_df.loc[:,:1175]

            
            #get the columns/features only relevant for the user
            #i.e. the selected features from step 1
            selected_column_names = [encoded_feature_cols[i] for i in selected_feature_indices]
            new_name_features = all_names_df.loc[:,selected_column_names[0]].values
            name_weights = all_names_weights.values
            
            print("Now preparing new cluster labels")
            updated_clusters = bc.get_cluster_labels(new_name_features,num_clusters=self.num_clusters, sample_weights=name_weights)
            print("Cluster lables recalculated.")
            print("now prepping cluster data for sqlite3")
            updated_clusters_prepped = self.prep_new_clusters_sql(updated_clusters,all_name_ids)
            print("Cluster labels prepped. Now saving to database")
            self.update_clusters_database(updated_clusters_prepped)
            print("Finished!")
            print("Duration: {}".format(time.time()-start))
            
            #for reference: the features most relevant to the user:
            rel_features = get_rel_features(selected_feature_indices[0])
            print("Relevant features: {}".format(", ".join(rel_features)))
            return True
        
        except RatingsOnlyOneKind:
            print("\nWe need more diverse ratings from you in order to recommend any names. \nYou'll find some you love or hate! Just keep rating.\n")

        return None
    
    def prep_new_clusters_sql(self,new_clusters,name_id_list):
        '''
        For reference, the SQL table COLUMNS:
        cluster_id INTEGER PRIMARY KEY, cluster INT, num_clusters INT, features_used TEXT, list_version INT, cluster_name_id INT, cluster_ratinglist_id INT
        '''
        version = str(int(self.list_version)+1)
        prepped_clusters = []
        for i in range(len(new_clusters)):
            prepped_clusters.append((str(new_clusters[i]),str(self.num_clusters),self.features_used,version,str(name_id_list[i]),str(self.list_id)))
        return prepped_clusters
    
#############################################################################
# recommend names
#############################################################################

    def get_cluster_name_dict(self):
        clusters_names = self.get_clusters_nameid()
        cluster_name_dict = {}
        for name in clusters_names:
            #set the name_id as key and cluster as value
            if name[0] not in cluster_name_dict:
                cluster_name_dict[name[0]] = name[1]
        return cluster_name_dict
    
    #def get_rated_names is a SQL function (see section above 'main functions')

    def sort_rated_names(self,rating_tuples):
        liked_name_ids = []
        for rating in rating_tuples:
            #name_id = index 0
            #rating = index 1
            if int(rating[1]) == 1:
                liked_name_ids.append(rating[0])
        return liked_name_ids
    
    def get_assigned_clusters(self,name_id_list,clusters_names_dict):
        assigned_clusters = []
        for name_id in name_id_list:
            assigned_clusters.append(clusters_names_dict[name_id])
        return assigned_clusters
    
    def get_recommended_name_ids(self,liked_clusters,nameid_cluster_dict):
        rec_name_ids = []
        #key = name_id, value = cluster
        for key, value in nameid_cluster_dict.items():
            if value in liked_clusters:
                rec_name_ids.append(key)
        return rec_name_ids
    
    #def get_names_nameids is SQL function
    
    def get_name_nameid_dict(self,names_tuple):
        name_id_dict = {}
        for nameset in names_tuple:
            #set the name_id as the key, name as the value
            name_id_dict[nameset[1]] = nameset[0]
        return name_id_dict
    
    def nameid_to_name(self,name_ids_list,name_id_dict):
        '''
        Find the values that match the liked name_ids 
        returns list of actual names
        '''
        names = []
        for name_id in name_ids_list:
            names.append(name_id_dict[name_id])
        shuffle(names)
        return names

    def collect_recommendation_ratings(self, rec_names):
        '''
        collects user's rating of each recommended name to determine score 
        user can save names they like
        '''
        num_names = 25
        print("These are the names we recommend.\nRate them: 1 or 0 \nSave them: Y or N")
        saved_names = []
        rated_names = {}
        try:
            for name in rec_names[:num_names]:
                print("\n~ {} ~\n".format(name))
                print("\nRating:")
                rating = input()
                if rating.isdigit():
                    if int(rating) == 1 or int(rating) == 0:
                        rated_names[name] = rating
                    if int(rating) == 1:
                        #if the user likes the name, ask if they want to save it
                        print("\nSave? (Y or N):")
                        save = input()
                        if save.isdigit():
                            print("Name not saved.")
                        elif "y" in save.lower():
                            saved_names.append((name,self.list_id))
                        elif "exit" in save.lower():
                            raise ExitFunction() 
                elif "exit" in rating.lower():
                    raise ExitFunction() 
        except ExitFunction:
            pass
        return rated_names, saved_names

    
