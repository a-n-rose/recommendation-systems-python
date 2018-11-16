import time
import sys
from extractfeatures_babynames import BuildTables, BuildFeatures
from build_clusters import BuildClusters


def main(database,num_clusters,features_used):
    try:
        bt = None
        # Connect to database and build tables for basic features
        bt = BuildTables(database)
        # get name_id, names, sex info
        names = bt.get_names()
        
        # use name data to build features
        bf = BuildFeatures()
        # get matrix with letter and length values 
        # and save dictionary with key vaues for column names (letters)
        # to the sql class so they can be saved as column names
        data = bf.define_features_letters_length(names)
        
        #save the data to the feature table
        #bt.save_basic_features(data)
        
        bc = BuildClusters()
        #starting out with 9 clusters: 5 for length of names and 4 for letter sound types (hard, soft, open, closed)
        for num in num_clusters:
            start = time.time()
            labels = bc.get_cluster_labels(data,num)
            prepped_clusters = bf.prep_defaultclusters_for_sql(names,labels,num,features_used)
            bt.create_default_clusters_table()
            bt.save_cluster_labels(prepped_clusters)
            end = time.time()
            duration = (end-start)
            print("Total duration to assign data to {} clusters: {} seconds".format(num,duration))
        return 1
    except Exception as e:
        print(e)
    finally:
        if bt:
            bt.conn.close()
        return 0
            
if __name__ == "__main__":
    database = "babynames_USA.db"
    num_clusters = [9,30,50]
    features_used = "original_letters_length"
    #sys.exit(main(database,num_clusters,features_used))
    print("Script deactivated. Are you sure you want to run this?")
