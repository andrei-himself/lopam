# crypto.py
import os 
from argon2.low_level import hash_secret_raw, Type
import nacl.bindings

def random_bytes(n: int) -> bytes:
    return os.urandom(n)

def derive_key(password_bytes: bytes, salt: bytes, mem_mb: int, iterations: int, parallelism: int) -> bytes:
    return hash_secret_raw(
        secret=password_bytes,
        salt=salt,
        time_cost=iterations,
        memory_cost=mem_mb * 1024,
        parallelism=parallelism,
        hash_len=32,
        type=Type.ID,
    )

def aead_encrypt(key: bytes, nonce: bytes, plaintext: bytes, ad: bytes) -> bytes:
    return nacl.bindings.crypto_aead_xchacha20poly1305_ietf_encrypt(plaintext, ad, nonce, key)

def aead_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, ad: bytes) -> bytes:
    return nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(ciphertext, ad, nonce, key)