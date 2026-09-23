
import logging
from sympy.crypto.crypto import rsa_private_key, rsa_public_key, encipher_rsa, decipher_rsa
from sympy import randprime

logging.basicConfig(level=logging.INFO)

def generate_rsa_keys(bits):
    """
    Generate RSA public and private keys.
    Note: Generating large keys (e.g., 2048 bits) can be slow.
    """
    logging.info(f"Generating RSA keys with {bits} bits.")
    p = randprime(2**(bits//2), 2**(bits//2 + 1))
    q = randprime(2**(bits//2), 2**(bits//2 + 1))
    n = p * q
    e = 65537
    private_key = rsa_private_key(p, q, e)
    public_key = rsa_public_key(n, e)
    return {"public_key": str(public_key), "private_key": str(private_key)}

def rsa_encrypt(public_key, message):
    """
    Encrypt a message using an RSA public key.
    """
    n_str, e_str = public_key.strip("()").split(",")
    n, e = int(n_str), int(e_str)
    message_int = int.from_bytes(message.encode(), 'big')
    encrypted_message = encipher_rsa(message_int, (n, e))
    return str(encrypted_message)

def rsa_decrypt(private_key, encrypted_message):
    """
    Decrypt a message using an RSA private key.
    """
    # SymPy returns private key as (n, d) tuple
    n_str, d_str = private_key.strip("()").split(",")
    n, d = int(n_str), int(d_str)
    encrypted_message_int = int(encrypted_message)
    decrypted_message_int = decipher_rsa(encrypted_message_int, (n, d))
    return decrypted_message_int.to_bytes((decrypted_message_int.bit_length() + 7) // 8, 'big').decode()
