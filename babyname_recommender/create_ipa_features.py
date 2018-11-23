'''
Create IPA letter features for names
IPA letters, lengths, stress information

'''
import time
import traceback
from ipa_features import IPA 



if __name__=="__main__":
    try:
        start = time.time()
        ipa = None
        database = "babynames_USA.db"
        ipa = IPA(database)
        ipa_features_dict = ipa.create_ipa_features()
        duration = time.time() - start
        print("Duration: {} sec".format(duration))
        
    except Exception as e:
        traceback.print_exception(e)
    finally:
        if ipa is not None:
            ipa.conn.close()
    
            

        
