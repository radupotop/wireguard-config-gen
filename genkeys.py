import base64
from pathlib import Path

import wgtools
import yaml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from models import HostModel, InterfaceModel, PeerModel
from yaml.loader import SafeLoader

interfaces_yaml = Path('interfaces.yaml')


def genkeypair() -> wgtools.Keypair:
    return wgtools.keypair()


def genpsk():
    return wgtools.genpsk()


def loadyaml():
    return yaml.load(interfaces_yaml.read_bytes(), Loader=SafeLoader)


def parseyaml():
    cfgdata = loadyaml()
    for ifname, ifdata in cfgdata['Machines'].items():
        print(ifname, HostModel.parse_obj(ifdata))


parseyaml()


def gen_keypair():
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
    return private_key_base64, public_key_base64
