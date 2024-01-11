from cryptography.fernet import Fernet
import os

class FernetEncryption:
    def __init__(self):
        key = os.getenv("FERNET_KEY")
        self.fernet = Fernet(key)

    def encrypt(self, message: str) -> bytes:
        return self.fernet.encrypt(message.encode())

    def decrypt(self, encrypted_message: bytes) -> str:
        return self.fernet.decrypt(encrypted_message).decode()
