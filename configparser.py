from pathlib import Path

import yaml
from models import HostModel, InterfaceModel, PeerModel
from yaml.loader import SafeLoader

interfaces_yaml = Path('interfaces.yaml')


def loadyaml():
    return yaml.load(interfaces_yaml.read_bytes(), Loader=SafeLoader)


def parseyaml():
    cfgdata = loadyaml()
    for ifname, ifdata in cfgdata['Machines'].items():
        print(ifname, ifdata)
        print(ifname, HostModel.model_validate(ifdata))


parseyaml()
