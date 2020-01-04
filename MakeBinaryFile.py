import pickle
from passlib.context import CryptContext

# Hashing configuration parameters
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)


def encrypt_password(password):
    """
    Hashes the raw input password and returns it
    :param password: the raw input password to encrypt
    :return: the hashed password
    """
    return pwd_context.encrypt(password)


# Binary file to hold hashed password in lieu of a database
output_file = open("passFile.bin", "wb")
pWord = encrypt_password("password")
pickle.dump(pWord, output_file)
output_file.close()
