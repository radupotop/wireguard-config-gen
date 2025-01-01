import base64
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from models import Keypair


def gen_keypair() -> Keypair:
    """
    Generate a private-public keypair natively with Python.
    """
    # Generate a private key
    private_key = X25519PrivateKey.generate()

    # Obtain the public key from the private key
    public_key = private_key.public_key()

    # Export the private key bytes
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Export the public key bytes
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    private_key_base64 = base64.b64encode(private_key_bytes).decode('utf-8').strip()
    public_key_base64 = base64.b64encode(public_key_bytes).decode('utf-8').strip()

    # Return the keys in base64 encoding
    return Keypair(public=public_key_base64, private=private_key_base64)


def gen_psk():
    """
    Generate a secure random 32-byte key.

    The preshared key (PSK) in WireGuard is different from the public/private key
    pair used in public key cryptography. The PSK is simply a randomly generated
    256-bit (32-byte) value that is used to add an additional layer of symmetric
    encryption on top of the standard WireGuard asymmetric encryption. It doesn't
    require elliptic curve operations like those performed with the X25519
    algorithm.
    """
    # Generate 32 random bytes
    random_bytes = os.urandom(32)
    # Encode the bytes in base64
    preshared_key = base64.b64encode(random_bytes).decode('utf-8').strip()
    return preshared_key
