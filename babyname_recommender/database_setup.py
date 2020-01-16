
import traceback
import time

from data_prep_babyname import Setup_Name_DB

'''
Saves name data from US social security applications to two basic tables in a database:
1) names table with name ID, name, sex
2) popularity table with year ID, year, popularity, name_ID (reference to names table)

names.zip should be extracted into a 'names' subdirectory. 
In other words, this script looks for .txt files in a subdirectory called 'names'.
'''

database = 'babynames_USA.db'

if __name__ == '__main__':
    try:
        bn = Setup_Name_DB(database)
        start = time.time()
        bn.create_table_names()
        bn.create_table_popularity()
        success = bn.collect_save_data()
        if success == True:
            print("Success!")
        else:
            print("Fail.")
        end = time.time()
        hours = round((end-start)/3600,4)
        print("Total time: {} hours".format(hours))
    except Exception as e:
        traceback.print_tb(e)
    finally:
        if bn.conn:
            bn.conn.close()
    
