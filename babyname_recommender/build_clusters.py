import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import KMeans
from sklearn import linear_model
from sklearn.feature_selection import RFE 
from sklearn.linear_model import LogisticRegression
#(n_clusters=8, init=’k-means++’, n_init=10, max_iter=300, tol=0.0001, precompute_distances=’auto’, verbose=0, random_state=None, copy_x=True, n_jobs=None, algorithm=’auto’)


class BuildClusters:

    def get_cluster_labels(self,feature_data,num_clusters=None, sample_weights = None):
        
        #to save memory: precompute_distances=False
        if num_clusters is not None:
            km = KMeans(n_clusters = num_clusters,precompute_distances=False)
        else:
            km = KMeans(precompute_distances=False)
        km.fit(feature_data,sample_weight = sample_weights)
        labels = km.labels_
        return labels
    
    def prune_features(self,X,y,num_features):
        model = LogisticRegression(solver='lbfgs')
        #removes half of the features if I don't put a number in
        #I have over 1,000 features, so I don't want that.
        #an int after model will return that many features (i.e. the best 3 or 10 etc. features)
        rfe = RFE(model,num_features)
        new_X = rfe.fit_transform(X,y)

        return new_X, rfe.support_
    
    def features_2_dict(self,features):
        name_feature_dict = {}
        for item in features:
            #don't include sex and ipa transcription at index 1 and 2
            name_feature_dict[item[0]] = [item[i+3] for i in range(len(item)-3)]
        #print("NAME FEATURE DICT: {}")
        return name_feature_dict
    
    def ratednames_features_2_dict(self,name_feature_dict,names_ratings):
        
        #create a new dict with only the ratings the user rated
        ratednames_dict = {}
        #name_rating_set[0] = name_id
        #name_rating_set[1] = rating
        for name_rating_set in names_ratings:
            #get the values (i.e. features) of each name rated
            #also append the rating the user gave the name
            name_id = name_rating_set[0]
            rating = name_rating_set[1]
            name_features = name_feature_dict[name_id]
            #expanded ipa has 1175 columns
            if len(name_features) == 1175:
                name_features.append(rating)
                ratednames_dict[name_id] = name_features
            else:
                print("Rating already present. No rating added. ")
        return ratednames_dict
    
    def dict2dataframe(self,dict_name_features,ratings = False, weight_name_ids=None):
        '''
        Function serves 2 purposes: 
        
        1) ratings = True:
        preps rated names and features for Reverse Feature Selection
        output: 
        * dataframe with features and ratings
        * name_ids list: the liked name ids to be used as weight identifiers for the other use of this function (reclustering with weights on liked names)
        
        2) ratings = False:
        preps all names, features, and weights for KMeans clustering 
        output:
        * dataframe with features and weights
        * name_ids list: helpful in saving new clusters in SQL
        '''
        liked_rows = None
        name_features_df = pd.DataFrame.from_dict(dict_name_features,orient='index')
        sorted_name_df = name_features_df.sort_index()
        
        if ratings:
            print("Identifying liked names.")
            rating_col = sorted_name_df.columns.values.tolist()[0]
            liked_nameids_series = sorted_name_df[rating_col] == 1
            name_ids = liked_nameids_series.index[liked_nameids_series].tolist()
        elif weight_name_ids:
            print("Creating weights for KMeans clustering.")
            sorted_name_df["weights"] = np.isin(sorted_name_df.index,weight_name_ids)
            #create weights: currently have disliked names with weight 1 and 
            #liked names with weight 10 (0 caused problems)
            sorted_name_df["weights"] = sorted_name_df["weights"].apply(lambda x: 10 if x is True else 1)
            
            name_ids = sorted_name_df.index.values.tolist()
            
            #make sure No NAN and fill with 1. 
            #if fill with zero, increase chances of Zero Division Error causing problems. 
            sorted_name_df= sorted_name_df.fillna(1)
        return sorted_name_df, name_ids

    def accuracy_recommendations(self,rec_dict_ratings):
        total = len(rec_dict_ratings)
        liked = 0
        for key, value in rec_dict_ratings.items():
            if int(value) == 1:
                liked+=1
        score = liked/float(total)*100
        return score
