import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import KMeans
from sklearn import linear_model
from sklearn.feature_selection import RFE 
from sklearn.linear_model import LogisticRegression
#(n_clusters=8, init=’k-means++’, n_init=10, max_iter=300, tol=0.0001, precompute_distances=’auto’, verbose=0, random_state=None, copy_x=True, n_jobs=None, algorithm=’auto’)


class BuildClusters:

    def get_cluster_labels(self,feature_data,num_clusters=None):

        #to save memory: precompute_distances=False
        if num_clusters is not None:
            km = KMeans(n_clusters = num_clusters,precompute_distances=False)
        else:
            km = KMeans(precompute_distances=False)
        km.fit(feature_data)
        labels = km.labels_
        return labels
    
    def prune_features(self,X,y):
        model = LogisticRegression(solver='lbfgs')
        #removes half of the features if I don't put a number in
        #otherwise, an int after model will return that many features (i.e. the best 3 or 10 etc. features)
        rfe = RFE(model)
        new_X = rfe.fit_transform(X,y)

        return new_X, rfe.support_, rfe.ranking_
    
    def features_2_dict(self,features):
        name_feature_dict = {}
        for item in features:
            name_feature_dict[item[0]] = [item[i+1] for i in range(len(item)-1)]
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
            #print(name_features)
            if name_features[-1] > 1:
                name_features.append(rating)
                #print(name_features)
                ratednames_dict[name_id] = name_features
            else:
                print("Repeat here?")
        #print(ratednames_dict)
        return ratednames_dict
    
    def dict2dataframe(self,dict_name_features):
        name_features_df = pd.DataFrame.from_dict(dict_name_features,orient='index')
        sorted_name_df = name_features_df.sort_index()
        return sorted_name_df
