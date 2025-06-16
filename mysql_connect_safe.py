import pymysql

from password_utils import get_decrypted_password

def connet_to_mysql():
    try:
        connection = pymysql.connect(
        host='localhost',
        user='root',
        password=get_decrypted_password(),
        db='airline',
        cursorclass=pymysql.cursors.DictCursor
        )
        print("work Done Boss")
        return connection

    except Exception as e:
        print(f"An error occurred while connecting to MySQL: {e}")
        return None


if __name__ == "__main__":
    connet_to_mysql()
             