'''
Babyname recommender
'''
import sys
from errors import ExitApp
from user_account import LoginUser
from user_data_babyname import UserData


def main(database,num_clusters,features_used):
    try:
        login = None
        ud = None
        login = LoginUser(database)
        login.sign_in()
        if login.is_user != True:
            print("Login failed.")
            raise ExitApp("UserId not found.")
        user_id = login.get_userid(login.username)
        if user_id is None:
            print("User ID Error")
            raise SystemExit
        ud = UserData(database,user_id,num_clusters,features_used)
        ud.main_menu()
        return 1
    except ExitApp:
        print("Have a good day!")
    except SystemExit as e:
        print("Problem occurred: {}. Had to close app.".format(e))
    finally:
        if login:
            login.conn.close()
        if ud:
            ud.conn.close()
        return 0

            
if __name__ == "__main__":
    database = "babynames_USA.db"
    num_clusters = 50
    features_used = "original_letters_length"
    sys.exit(main(database,num_clusters,features_used))
