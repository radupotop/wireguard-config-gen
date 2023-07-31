from pathlib import Path

import wgtools
import yaml
from yaml.loader import SafeLoader

from models import HostModel, InterfaceModel, PeerModel

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
