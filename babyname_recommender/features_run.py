import time
import traceback
import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from extractfeatures_babynames import BuildTables, BuildFeatures
from build_clusters import BuildClusters

            
if __name__ == "__main__":
    database = "babynames_USA.db"
    num_clusters = [30]
    features_used = "features_ipa_extended" #options: "original_letters_length"  "ipa_chars_length"  "features_ipa_extended"


    try:
        bt = None
        # Connect to database and build tables for basic features
        bt = BuildTables(database)
        # get name_id, names, sex info
        names = bt.get_names()
        
        # use name data to build features
        bf = BuildFeatures()
        bc = BuildClusters()
        # get matrix with letter and length values 
        # and save dictionary with key vaues for column names (letters)
        # to the sql class so they can be saved as column names
        
        if features_used == "original_letters_length":
            data = bf.define_features_letters_length(names)
            #already saved the basic features...
            #save the data to the feature table
            #bt.save_basic_features(data)
            
            #first column is name_id
            features = data[:,1:]
            print("one-hot-encoding features")
            
            #onehotencode length
            #specify how many categories for each feature expected
            categories = []
            for i in range(26):
                categories.append(([0,1]))
            categories.append(([2,3,4,5,6,7,8,9,10,11,12,13,14,15]))
            enc = OneHotEncoder(categories=categories,sparse=False)
            new_features = enc.fit_transform(features)
        
        else:
            if features_used == "ipa_chars_length":
                features = bt.get_basic_ipa_features()
            elif features_used == "features_ipa_extended":
                features = bt.get_extended_ipa_features()
            features_dict = bc.features_2_dict(features)
            new_features_df, name_ids = bc.dict2dataframe(features_dict)
            new_features = new_features_df.values
        
        for num in num_clusters:
            start = time.time()
            print("Fitting clusters to data")
            labels = bc.get_cluster_labels(new_features,num)
            print("Labels done")
            prepped_clusters = bf.prep_defaultclusters_for_sql(names,labels,num,features_used)
            print("prepped_clusters")
            bt.create_default_clusters_table()
            print("created table")
            bt.save_cluster_labels(prepped_clusters)
            print("saved_cluster_labels")
            end = time.time()
            duration = (end-start)
            print("Total duration to assign data to {} clusters: {} seconds".format(num,duration))

    except Exception as e:
        traceback.print_exception(e)
        print(e)
    finally:
        if bt:
            bt.conn.close()

