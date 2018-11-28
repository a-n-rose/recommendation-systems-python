'''
Create IPA letter features for names
IPA letters, lengths, stress information

'''
import time
import traceback
from ipa_features import IPA 
from errors import IPAnotAligned



if __name__=="__main__":
    try:
        start = time.time()
        ipa = None
        database = "babynames_USA.db"
        ipa = IPA(database)
        new_features, cols = ipa.create_ipa_features()
        print(new_features)
        print(cols)
        duration = time.time() - start
        print("Duration: {} sec".format(duration))
        
    except IPAnotAligned as e:
        print(e)
    except Exception as e:
        traceback.print_exception(e)
    finally:
        if ipa is not None:
            ipa.conn.close()
    
            

        
