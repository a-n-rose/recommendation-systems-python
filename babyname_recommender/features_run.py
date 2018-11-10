import traceback
from extractfeatures_babynames import BuildTables, BuildFeatures
database = "babynames_USA.db"
if __name__=="__main__":
    try:
        # Connect to database and build tables for basic features
        bt = BuildTables(database)
        # get name_id, names, sex info
        names = bt.get_names()
        
        # use name data to build features
        bf = BuildFeatures()
        # get matrix with letter and length values 
        # and save dictionary with key vaues for column names (letters)
        # to the sql class so they can be saved as column names
        data, bt.letters_int_dict = bf.define_features_letters_length(names)
        
        #save the data to the feature table
        bt.save_basic_features(data)

    except Exception as e:
        print(e)
        traceback.print_tb(e)
    finally:
        if bt.conn:
            bt.conn.close()
        
    
