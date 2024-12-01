from cryptography.fernet import Fernet
from typing import Tuple
import base64
from app.core.config import Settings

class EncryptionService:
    def __init__(self, settings: Settings):
        self.master_key = settings.ENCRYPTION_MASTER_KEY.encode()
        self.master_fernet = Fernet(self.master_key)
    
    def encrypt_content(self, content: str) -> Tuple[str, str]:
        # Generate a unique key for this content
        content_key = Fernet.generate_key()
        content_fernet = Fernet(content_key)
        
        # Encrypt the content
        encrypted_content = content_fernet.encrypt(content.encode())
        
        # Encrypt the content key with master key
        encrypted_key = self.master_fernet.encrypt(content_key)
        
        return base64.b64encode(encrypted_content).decode(), base64.b64encode(encrypted_key).decode()
    
    def decrypt_content(self, encrypted_content: str, encrypted_key: str) -> str:
        # Decode from base64
        encrypted_content_bytes = base64.b64decode(encrypted_content)
        encrypted_key_bytes = base64.b64decode(encrypted_key)
        
        # Decrypt the content key
        content_key = self.master_fernet.decrypt(encrypted_key_bytes)
        
        # Decrypt the content
        content_fernet = Fernet(content_key)
        decrypted_content = content_fernet.decrypt(encrypted_content_bytes)
        
        return decrypted_content.decode()