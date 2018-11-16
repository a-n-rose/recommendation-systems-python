import sqlite3
from errors import ExitApp
from random import shuffle

class UserData:
    def __init__(self,database,user_id,num_clusters,features_used):
        self.database = database
        self.user_id = user_id
        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()
        self.ratinglists = self.access_ratinglist_table()
        self.num_clusters = num_clusters
        self.features_used = features_used
        
####################### SQL FUNCTIONS #########################################

# CREATE/INITIATE TABLES

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
    
    def access_user_clusters_table(self):
        msg = '''CREATE TABLE IF NOT EXISTS users_clusters(cluster_id INTEGER PRIMARY KEY, cluster INT, num_clusters INT, features_used TEXT, cluster_name_id INT, cluster_ratinglist_id INT, FOREIGN KEY(cluster_name_id) REFERENCES names(name_id), FOREIGN KEY(cluster_ratinglist_id) REFERENCES ratinglists(ratinglist_id)) '''
        self.c.execute(msg)
        self.conn.commit()

# INSERT STATEMENTS
    
    def initiate_default_clusters(self, default_clusters):
        msg = '''INSERT INTO users_clusters VALUES(NULL, ?, ?, ?, ?, ?) '''
        self.c.executemany(msg,default_clusters)
        self.conn.commit()
        return None
    
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
    
    def save_rated_names(self,prepped_list):
        msg = '''INSERT INTO ratings VALUES(NULL,?,?,?) '''
        self.c.executemany(msg,prepped_list)
        self.conn.commit()
        return None
    
# SELECT STATEMENTS ( 1) lists, 2) clusters, 3) names )
    
    def get_lists(self):
        t = (self.user_id,)
        msg = '''SELECT * FROM ratinglists WHERE ratinglist_user_id=? '''
        self.c.execute(msg,t)
        lists = self.c.fetchall()
        return lists
    
    def get_list_id(self):
        t = (self.listchoice,self.user_id,)
        msg = '''SELECT ratinglist_id FROM ratinglists WHERE ratinglist_order=? AND ratinglist_user_id=? '''
        self.c.execute(msg,t)
        list_id = self.c.fetchall()
        if len(list_id) == 0:
            return None
        self.list_id = list_id[0][0]
        return list_id[0][0]
    
    def check_for_clusters(self):
        self.access_user_clusters_table()
        t = (self.get_list_id(),self.num_clusters,self.features_used)
        msg = '''SELECT cluster FROM users_clusters WHERE cluster_ratinglist_id=? AND num_clusters=? AND features_used=? LIMIT 10 '''
        self.c.execute(msg,t)
        clusters = self.c.fetchall()
        if len(clusters) == 10:
            return True
        else:
            return False
        return None
    
#cluster INT, num_clusters INT, features_used TEXT, cluster_name_id INT, cluster_ratinglist_id INT,
        
    
    def collect_default_clusters(self):
        t = (self.num_clusters,self.features_used)
        msg = '''SELECT cluster, num_clusters, features_used, cluster_name_id FROM default_clusters WHERE num_clusters=? AND features_used=? '''
        self.c.execute(msg,t)
        clusters = self.c.fetchall()
        return clusters

    
    def get_clusters_nameid(self):
        t = (str(self.list_id),)
        msg = '''SELECT cluster_name_id, cluster FROM users_clusters WHERE cluster_ratinglist_id=? '''
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
        t = (self.listchoice,self.user_id,)
        msg = '''SELECT babyname_type FROM ratinglists WHERE ratinglist_order=? AND ratinglist_user_id=? '''
        self.c.execute(msg,t)
        babyname_type = self.c.fetchall()
        return babyname_type[0][0]
    
    def get_rated_names(self):
        t = (str(self.list_id),)
        msg = '''SELECT rating_name_id,rating FROM ratings WHERE rating_ratinglist_id=? '''
        self.c.execute(msg,t)
        ratings = self.c.fetchall()
        return ratings
    
    def get_names_nameids(self):
        msg = '''SELECT name, name_id FROM names '''
        self.c.execute(msg)
        names = self.c.fetchall()
        return names
    

####################### MAIN FUNCTIONS THAT CALL OTHER FUNCTIONS #########################################
    
    def main_menu(self):
        print("\nMAIN MENU\n")
        self.show_options_main()
        choice = self.choose_options_main()
        if choice is None:
            raise ExitApp("User exited the program.")
        if 1 == int(choice):
            self.show_and_choose_lists()
            self.activate_clusters()
            self.rate_names()
            self.main_menu()
        elif 2 == int(choice):
            self.show_and_choose_lists()
            self.activate_clusters()
            self.recommend_names()
            self.main_menu()
        else:
            print("Please choose the corresponding digit.")
            self.main_menu()
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
    
    def create_new_ratinglist(self):
        list_name = self.get_list_name()
        self.show_nametype_options()
        babyname_type = self.choose_babyname_type()
        self.save_list(list_name,babyname_type)
        lists_actualized = self.get_lists()
        self.make_list_dict(lists_actualized)
        self.set_mostrecentlist_as_listchoice()
        self.access_user_clusters_table()
        self.initiate_default_clusters()
        self.rate_names()
        return None
    
    def rate_names(self):
        rated_names_dict = self.collect_name_ratings()
        prepped_list = self.prep_rating_names_dict(rated_names_dict)
        self.save_rated_names(prepped_list)
        return None

    def recommend_names(self):
        #create dictionary containing the current clusters assigned to each name (according to the search list)
        nameid_cluster_dict = self.get_cluster_name_dict()
        
        #collect the ratings the user has made so far (according to the search list)
        ratings = self.get_rated_names()
        
        #separate liked from disliked names - see how well the clusters are separating these
        liked_name_ids, disliked_name_ids = self.sort_rated_names(ratings)
        liked_clusters = self.get_matched_clusters(liked_name_ids,nameid_cluster_dict)
        disliked_clusters = self.get_matched_clusters(disliked_name_ids,nameid_cluster_dict)
        similarity = self.check_cluster_list_similarity(liked_clusters,disliked_clusters)
        if similarity is not None:
            if similarity > 0.25:
                print("\nWARNING: Clusters for liked and disliked names have high overlap")
            print("Similarity of cluster likes and dislikes: {}\n".format(similarity))
        else:
            print("\nProblem with cluster comparison. No liked clusters found.\n")
        
        #build recommendations based on cluster numbers --> recommend names with same cluster number
        rec_name_ids = self.get_recommended_name_ids(liked_clusters,nameid_cluster_dict)
        name_id_tuple = self.get_names_nameids()
        name_id_dict = self.get_name_nameid_dict(name_id_tuple)
        rec_names = self.nameid_to_name(rec_name_ids,name_id_dict)
        print("\nRecommended Names for you: \n\n{}".format("\n".join(rec_names[:50])))
        return None
           
####################### SUPPORT FUNCTIONS CALLED BY MAIN FUNCTIONS #########################################

# def main menu

    def show_options_main(self):
        print("1) rate names\n2) see recommendations\n")
        return None
    
    def choose_options_main(self):
        choice = input()
        if choice.isdigit():
            return choice
        elif 'exit' in choice.lower():
            return None
        print("Please enter the corresponding digit or type 'exit'.")
        self.choose_options_main()

    def activate_clusters(self):
        self.access_user_clusters_table()
        #check if clusters exist 
        clusters_exist = self.check_for_clusters()
        if clusters_exist is False:
            default_clusters = self.collect_default_clusters()
            prepped_default_clusters = self.prep_default_clusters(default_clusters)
            self.initiate_default_clusters(prepped_default_clusters)
        return None
    
    def prep_default_clusters(self,default_clusters_list):
        default_clusters = []
        list_id = self.get_list_id()
        for cluster in default_clusters_list:
            default_clusters.append((cluster[0],cluster[1],cluster[2],cluster[3],list_id))
        return default_clusters
        
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
    
    def get_list_choice(self):
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
    
# rate_names

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
                    rating_dict[names[i][0]] = rating
        return rating_dict
    
    def prep_rating_names_dict(self,rated_names_dict):
        list_id = self.get_list_id()
        prepped_list = []
        for key, value in rated_names_dict.items():
            prepped_list.append((int(value),list_id,key))
        return prepped_list
    
# recommend_names

    def sort_rated_names(self,rating_tuples):
        liked_name_ids = []
        disliked_name_ids = []
        for rating in rating_tuples:
            #name_id = index 0
            #rating = index 1
            if int(rating[1]) == 1:
                liked_name_ids.append(rating[0])
            else:
                disliked_name_ids.append(rating[0])
        return liked_name_ids, disliked_name_ids
    
    def get_cluster_name_dict(self):
        clusters_names = self.get_clusters_nameid()
        cluster_name_dict = {}
        for name in clusters_names:
            #set the name_id as key and cluster as value
            if name[0] not in cluster_name_dict:
                cluster_name_dict[name[0]] = name[1]
        return cluster_name_dict
    
    def get_matched_clusters(self,name_id_list,clusters_names_dict):
        matched_clusters = []
        for name_id in name_id_list:
            matched_clusters.append(clusters_names_dict[name_id])
        return matched_clusters
    
    def check_cluster_list_similarity(self,clusterlist1,clusterlist2):
        total_len_cluster1 = len(clusterlist1)
        sim = 0
        for cluster in clusterlist1:
            if cluster in clusterlist2:
                sim+=1
        if total_len_cluster1 > 0:
            similarity = sim/float(total_len_cluster1)
            return similarity
        return None
    
    def get_recommended_name_ids(self,liked_clusters,nameid_cluster_dict):
        rec_name_ids = []
        #key = name_id, value = cluster
        for key, value in nameid_cluster_dict.items():
            if value in liked_clusters:
                rec_name_ids.append(key)
        return rec_name_ids
    
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
