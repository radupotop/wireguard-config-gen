import itertools
from ipaddress import IPv4Interface
from pathlib import Path

import yaml
from genkeys import gen_keypair, gen_psk
from models import InterfaceModel, PeerModel, YamlConfig
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
    prefixlen = cfgdata.DynStartIP.network.prefixlen
    cnt = itertools.count()
    if not cfgdata.PresharedKey:
        cfgdata.PresharedKey = gen_psk()
    for ifname, ifdata in cfgdata.Machines.items():
        if not ifdata.Interface:
            ifdata.Interface = InterfaceModel()
        if not ifdata.Peer:
            ifdata.Peer = PeerModel()
        # Set a dynamic Interface address if none specified
        if not ifdata.Interface.Address:
            ifdata.Interface.Address = IPv4Interface(
                f"{cfgdata.DynStartIP.ip + next(cnt)}/{prefixlen}"
            )
        # Set the Peer allowed IP to be the same as the Interface address
        # if none specified, but with prefixlen /32.
        if not ifdata.Peer.AllowedIPs:
            ifdata.Peer.AllowedIPs = [IPv4Interface(ifdata.Interface.Address.ip)]
        if not ifdata.Peer.PresharedKey:
            ifdata.Peer.PresharedKey = cfgdata.PresharedKey
        # Generate keypair if none specified
        if not ifdata.Interface.PrivateKey:
            keypair = gen_keypair()
            ifdata.Interface.PrivateKey = keypair.private
            ifdata.Peer.PublicKey = keypair.public
    print(cfgdata)
    Path('result.yaml').write_text(
        yaml.dump(cfgdata.model_dump(mode='json', exclude_none=True))
    )


parseyaml()
