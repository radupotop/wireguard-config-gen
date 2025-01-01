import itertools
from ipaddress import IPv4Interface
from pathlib import Path
from pprint import pprint

import yaml
from genkeys import gen_keypair, gen_psk
from models import InterfaceModel, PeerModel, WireguardConfig, YamlConfig
from yaml.loader import SafeLoader


def parse_to_wg_config(start_with: str, cfgdata: YamlConfig) -> WireguardConfig:
    wgconf = WireguardConfig()
    wgconf.Interface = cfgdata.Machines[start_with].Interface

    for ifname, ifdata in cfgdata.Machines.items():
        if ifname != start_with:
            wgconf.Peers.append(ifdata.Peer)

    pprint(wgconf.model_dump(mode='json', exclude_none=True))
    return wgconf


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

    raw_cfgdata = cfgdata.model_dump(mode='json', exclude_none=True)
    pprint(raw_cfgdata)
    Path('result.yaml').write_text(yaml.dump(raw_cfgdata))

    parse_to_wg_config('S23', cfgdata)


parseyaml()
