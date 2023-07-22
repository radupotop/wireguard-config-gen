import yaml
import wgtools
from yaml.loader import SafeLoader
from pathlib import Path
from models import HostModel

interfaces_yaml = Path('interfaces.yaml')

def genkeypair() -> wgtools.Keypair:
    return wgtools.keypair()

def genpsk():
    return wgtools.genpsk()

def loadyaml():
    return yaml.load(interfaces_yaml.read_bytes(), Loader=SafeLoader)

def parseyaml():
    cfgdata = loadyaml()
    for ifname, ifdata in cfgdata['Hosts'].items():
        print(HostModel.parse_obj(ifdata))

parseyaml()
