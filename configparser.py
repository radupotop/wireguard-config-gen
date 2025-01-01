from ipaddress import IPv4Interface
from pathlib import Path

import yaml
from genkeys import gen_keypair
from models import PeerModel, YamlConfig
from yaml.loader import SafeLoader


def loadyaml(filepath: str):
    """
    Load a YAML file.
    """
    yaml_file = Path(filepath)
    return yaml.load(yaml_file.read_bytes(), Loader=SafeLoader)


def parseyaml():
    yaml_contents = loadyaml('interfaces.yaml')
    cfgdata = YamlConfig.model_validate(yaml_contents)
    for ifname, ifdata in cfgdata.Machines.items():
        # print('orig', ifname, ifdata)
        if not ifdata.Peer:
            ifdata.Peer = PeerModel()
        if not ifdata.Peer.AllowedIPs:
            # cast Interface Address to /32
            ifdata.Peer.AllowedIPs = [IPv4Interface(ifdata.Interface.Address.ip)]
        if not ifdata.Interface.PrivateKey:
            keypair = gen_keypair()
            ifdata.Interface.PrivateKey = keypair.private
            ifdata.Peer.PublicKey = keypair.public
    print(cfgdata)
    Path('result.yaml').write_text(yaml.dump(cfgdata.model_dump(mode='json')))


parseyaml()
