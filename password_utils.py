from cryptography.fernet import Fernet


class fakestr (str):
    def __str__(self):
        return "********"
    def __repr__(self):
        return "********"

def load_password ():
    return open ("secert_key.key","rb").read()

def encrypted():
    encrypted=encrypt_password("Kausik")
    return encrypted

def encrypt_password (password):
    key=load_password()
    f=Fernet(key)
    return  f.encrypt(password.encode())

def decrypt_password (encrypted_password):
    key=load_password()
    f=Fernet(key)
    decryption= f.decrypt(encrypted_password).decode()    
    return fakestr(decryption)

def get_decrypted_password ():
    encrypt_password= encrypted()
    return decrypt_password(encrypt_password)
