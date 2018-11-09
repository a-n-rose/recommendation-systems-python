'''
Babyname recommender
'''
from errors import ExitApp
from user_account import UserAccount
from user_data_babyname import BabynameRecommender


if __name__ == "__main__":
    try:
        database = 'babynames_USA.db'
        user = UserAccount(database)
        user.sign_in()
        if user.is_user != True:
            print("Login failed.")
            raise ExitApp("UserId not found.")
        user_id = user.get_userid(user.username)
        if user_id is None:
            print("User ID Error")
            raise SystemExit
        user.close()
        bn = BabynameRecommender(database,user_id)
        bn.main_menu()
    except ExitApp:
        print("Have a good day!")
    except SystemExit as e:
        print("Problem occurred: {}. Had to close app.".format(e))
    finally:
        if user.conn:
            user.conn.close()
        elif bn.conn:
            bn.conn.close()

            
