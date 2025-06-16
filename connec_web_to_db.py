from sqlalchemy import create_engine
from password_utils import get_decrypted_password

def db_connect():
    username = 'root'
    password = "Kausik"
    host = 'localhost'
    database = 'airline'
    port = 3306 
    engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')
    return engine
        
        # Test connection
        