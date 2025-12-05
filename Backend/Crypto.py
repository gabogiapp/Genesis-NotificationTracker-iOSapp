from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
import binascii
from binascii import unhexlify
from typing import List


class Crypto:
    """Small crypto helpers used by the project.

    Notes:
      - The existing code uses AES-ECB in `encrypt_string`/`decrypt_string`.
        AES-ECB is not semantically secure and should be avoided for new data.
        To preserve compatibility we keep the current behavior but add
        validation and documentation.
    """

    @staticmethod
    def _validate_key_bytes(key_bytes: bytes) -> None:
        """Ensure `key_bytes` has a supported AES length (16, 24, 32 bytes)."""
        if len(key_bytes) not in (16, 24, 32):
            raise ValueError("AES key must be 16, 24, or 32 bytes long")

    @staticmethod
    def encrypt_string(plaintext: str, key: str) -> str:
        """Encrypt `plaintext` using AES-ECB and return a hex string.

        This preserves the repository's original behavior but validates key
        length to avoid runtime cryptography errors.
        """
        key_data = key.encode("utf-8")
        Crypto._validate_key_bytes(key_data)
        plaintext_data = plaintext.encode("utf-8")

        cipher = Cipher(algorithms.AES(key_data), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        # Original code used left-justified padding to 16 bytes; keep behavior
        padded_plaintext_data = plaintext_data.ljust(16)
        encrypted_bytes = encryptor.update(padded_plaintext_data) + encryptor.finalize()
        encrypted_hex_string = binascii.hexlify(encrypted_bytes).decode("utf-8")
        return encrypted_hex_string

    @staticmethod
    def decrypt_string(ciphertext: str, key: str) -> str:
        """Decrypt hex `ciphertext` that was encrypted with `encrypt_string`.

        The implementation mirrors `encrypt_string` and strips trailing NUL
        bytes added by the left-justify padding.
        """
        key_data = key.encode("utf-8")
        Crypto._validate_key_bytes(key_data)
        ciphertext_data = binascii.unhexlify(ciphertext)

        cipher = Cipher(algorithms.AES(key_data), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_bytes = decryptor.update(ciphertext_data) + decryptor.finalize()
        decrypted_string = decrypted_bytes.rstrip(b"\0").decode("utf-8", errors="ignore")
        return decrypted_string

    @staticmethod
    def decrypt_fcm_token(ciphertext: str, key: str) -> str:
        """Decrypt an FCM token encrypted with AES-CBC using PyCryptodome.

        The ciphertext is expected to be hex-formatted and to contain the IV
        as the first AES.block_size bytes.
        """
        key_bytes = key.encode("utf-8")
        Crypto._validate_key_bytes(key_bytes)
        ciphertext_bytes = unhexlify(ciphertext)
        iv = ciphertext_bytes[: AES.block_size]
        ciphertext_body = ciphertext_bytes[AES.block_size :]
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext_body), AES.block_size)
        return plaintext.decode("utf-8")

    @staticmethod
    def split_string(string: str, chunk_size: int) -> List[str]:
        return [string[i : i + chunk_size] for i in range(0, len(string), chunk_size)]
