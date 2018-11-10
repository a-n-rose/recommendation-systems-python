import traceback
from extractfeatures_babyname import LettersLength
database = "babynames_USA.db"
if __name__=="__main__":
    try:

        llf = LettersLength(database)
        llf.define_features_letters_length()

    except Exception as e:
        print(e)
        traceback.print_tb(e)
    finally:
        if llf.conn:
            llf.conn.close()
        
    
