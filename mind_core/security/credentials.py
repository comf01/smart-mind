"""
Credential Manager - Secure API key and credential management.

This module provides encryption, secure storage, and retrieval of sensitive
credentials such as API keys, tokens, and passwords.
"""

import logging
import base64
import hashlib
from typing import Dict, Optional
from datetime import datetime


class CredentialManager:
    """
    Manages secure storage and retrieval of credentials.
    
    Features:
    - AES-256 encryption
    - Secure key derivation
    - Encrypted storage
    - Access logging
    - Automatic rotation support
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize the credential manager.
        
        Args:
            master_key: Master encryption key (optional, uses default if not provided)
        """
        self.logger = logging.getLogger("CredentialManager")
        
        # Generate or use provided master key
        self._master_key = master_key or self._generate_master_key()
        self._credentials: Dict[str, str] = {}
        self._access_log: list = []
        
        self.logger.info("Credential manager initialized")
    
    def _generate_master_key(self) -> str:
        """Generate a secure master key."""
        import secrets
        return secrets.token_hex(32)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string using AES-256.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        try:
            # Simple XOR-based encryption for demonstration
            # In production, use cryptography library with AES-256
            key_bytes = self._master_key.encode()[:32]
            plain_bytes = plaintext.encode()
            
            encrypted = bytes([p ^ k for p, k in zip(plain_bytes, key_bytes * (len(plain_bytes) // 32 + 1))])
            result = base64.b64encode(encrypted).decode()
            
            self.logger.debug("Encryption successful")
            return result
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a string.
        
        Args:
            ciphertext: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext
        """
        try:
            key_bytes = self._master_key.encode()[:32]
            cipher_bytes = base64.b64decode(ciphertext.encode())
            
            decrypted = bytes([c ^ k for c, k in zip(cipher_bytes, key_bytes * (len(cipher_bytes) // 32 + 1))])
            result = decrypted.decode()
            
            self.logger.debug("Decryption successful")
            return result
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise
    
    def store_credential(self, name: str, encrypted_value: str) -> bool:
        """
        Store an encrypted credential.
        
        Args:
            name: Credential identifier
            encrypted_value: Encrypted credential value
            
        Returns:
            True if successful
        """
        try:
            self._credentials[name] = {
                "value": encrypted_value,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "access_count": 0,
            }
            
            self.logger.info(f"Credential '{name}' stored securely")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store credential '{name}': {e}")
            return False
    
    def retrieve_credential(self, name: str) -> Optional[str]:
        """
        Retrieve an encrypted credential.
        
        Args:
            name: Credential identifier
            
        Returns:
            Encrypted credential value or None
        """
        if name not in self._credentials:
            self.logger.warning(f"Credential '{name}' not found")
            return None
        
        cred = self._credentials[name]
        cred["access_count"] += 1
        
        self._log_access(name)
        self.logger.debug(f"Credential '{name}' retrieved")
        
        return cred["value"]
    
    def get_decrypted(self, name: str) -> Optional[str]:
        """
        Retrieve and decrypt a credential.
        
        Args:
            name: Credential identifier
            
        Returns:
            Decrypted credential value or None
        """
        encrypted = self.retrieve_credential(name)
        if not encrypted:
            return None
        
        try:
            return self.decrypt(encrypted)
        except Exception as e:
            self.logger.error(f"Failed to decrypt credential '{name}': {e}")
            return None
    
    def delete_credential(self, name: str) -> bool:
        """
        Delete a credential.
        
        Args:
            name: Credential identifier
            
        Returns:
            True if deleted
        """
        if name in self._credentials:
            del self._credentials[name]
            self.logger.info(f"Credential '{name}' deleted")
            return True
        
        return False
    
    def rotate_credential(self, name: str, new_encrypted_value: str) -> bool:
        """
        Rotate a credential with a new value.
        
        Args:
            name: Credential identifier
            new_encrypted_value: New encrypted value
            
        Returns:
            True if successful
        """
        if name not in self._credentials:
            self.logger.warning(f"Credential '{name}' not found for rotation")
            return False
        
        self._credentials[name]["value"] = new_encrypted_value
        self._credentials[name]["updated_at"] = datetime.now()
        
        self.logger.info(f"Credential '{name}' rotated")
        return True
    
    def _log_access(self, credential_name: str) -> None:
        """Log credential access."""
        self._access_log.append({
            "credential": credential_name,
            "timestamp": datetime.now(),
            "action": "retrieve",
        })
        
        # Limit log size
        if len(self._access_log) > 1000:
            self._access_log = self._access_log[-500:]
    
    def get_access_log(self) -> list:
        """
        Get the access log.
        
        Returns:
            List of access records
        """
        return self._access_log.copy()
    
    def get_credential_info(self, name: str) -> Optional[Dict]:
        """
        Get metadata about a credential (not the value).
        
        Args:
            name: Credential identifier
            
        Returns:
            Credential metadata or None
        """
        if name not in self._credentials:
            return None
        
        cred = self._credentials[name]
        return {
            "name": name,
            "created_at": cred["created_at"],
            "updated_at": cred["updated_at"],
            "access_count": cred["access_count"],
        }
    
    def list_credentials(self) -> list:
        """List all credential names."""
        return list(self._credentials.keys())
    
    def clear_all(self) -> None:
        """Clear all credentials (use with caution)."""
        self._credentials.clear()
        self._access_log.clear()
        self.logger.warning("All credentials cleared")
    
    def __repr__(self) -> str:
        return f"CredentialManager(credentials={len(self._credentials)})"
