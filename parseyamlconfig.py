import itertools
from ipaddress import IPv4Interface
from pathlib import Path
from pprint import pprint

import yaml
from genkeys import gen_keypair, gen_psk
from models import InterfaceModel, PeerModel, YamlConfig
from parsewgconfig import parse_to_wg_config, wg_config_to_ini
from yaml.loader import SafeLoader

OUTDIR = Path('output/')


def load_yaml(filepath: str):
    """
    Load a YAML file.
    """
    yaml_file = Path(filepath)
    if not yaml_file.exists():
        raise RuntimeError(f'Missing file - {filepath}')
    return yaml.load(yaml_file.read_bytes(), Loader=SafeLoader)


def merge_yaml(*filepaths: str) -> dict:
    """
    Merge multiple YAML files.
    Latter files will inherit and override the former files.
    """
    merged_data = dict()
    for _fpath in filepaths:
        _fcontent = load_yaml(_fpath)
        merged_data.update(_fcontent)
    return merged_data


def parse_yaml_config(yaml_contents: dict):
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
    (OUTDIR / 'result.yaml').write_text(yaml.dump(raw_cfgdata))

    for ifname in cfgdata.Machines.keys():
        wgconf = parse_to_wg_config(ifname, cfgdata)
        ini = wg_config_to_ini(ifname, wgconf)
        (OUTDIR / ifname).with_suffix('.conf').write_text(ini)


yaml_contents = merge_yaml('interfaces.yaml', 'output/result.yaml')
parse_yaml_config(yaml_contents)
