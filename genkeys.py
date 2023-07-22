import yaml
import wgtools


def genkeypair() -> wgtools.Keypair:
    return wgtools.keypair()

def genpsk():
    return wgtools.genpsk()

