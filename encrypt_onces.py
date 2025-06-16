from cryptography.fernet import Fernet


def generate_key():
    key=Fernet.generate_key()
    with open('secert_key.key', 'wb') as key_file:
        key_file.write(key)
        print("Key generated and saved to 'input/secert_key.key'.")

                                        

if __name__ == "__main__":
    try:
        generate_key()
        print("Key generation complete.")        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Key generation failed.")
    finally:
        print("Exiting the key generation process.")
        