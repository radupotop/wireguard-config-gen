from ipaddress import IPv4Interface
from pathlib import Path
from pprint import pprint
from typing import TextIO
from itertools import combinations

import yaml
from genkeys import gen_keypair, gen_psk
from models import InterfaceModel, PeerModel, YamlConfig
from parsewgconfig import parse_to_wg_config, wg_config_to_ini

OUTDIR = Path('output/')


def load_yaml(filebuf: TextIO):
    """
    Load a YAML file.
    """
    return yaml.safe_load(filebuf.read())


def recursive_update(dict1, dict2):
    """
    Recursively update dictionary `dict1` with `dict2`.
    """
    for key, value in dict2.items():
        if isinstance(value, dict) and key in dict1 and isinstance(dict1[key], dict):
            # If both values are dictionaries, recurse
            recursive_update(dict1[key], value)
        else:
            # Otherwise, overwrite dict1's key with dict2's value
            dict1[key] = value


def merge_yaml(filebuf_list: list[TextIO]) -> dict:
    """
    Merge multiple YAML files.
    Latter files will inherit and override the former files.
    """
    merged_data = dict()
    for _buf in filebuf_list:
        _fcontent = load_yaml(_buf)
        recursive_update(merged_data, _fcontent)
    return merged_data


def parse_yaml_config(yaml_contents: dict):
    cfgdata = YamlConfig.model_validate(yaml_contents)
    for ifname, ifdata in cfgdata.Machines.items():
        if not ifdata.Interface:
            ifdata.Interface = InterfaceModel()
        if not ifdata.Peer:
            ifdata.Peer = PeerModel()
        # Set a dynamic Interface address if none specified
        if not ifdata.Interface.Address:
            ifdata.Interface.Address = IPv4Interface(
                f"{cfgdata.Dynamic.StartIP}/{cfgdata.Dynamic.PrefixLen}"
            )
            cfgdata.Dynamic.StartIP += 1
        # Set the Peer allowed IP to be the same as the Interface address
        # if none specified, but with prefixlen /32.
        if not ifdata.Peer.AllowedIPs:
            ifdata.Peer.AllowedIPs = [IPv4Interface(ifdata.Interface.Address.ip)]
        # Generate keypair if none specified
        if not ifdata.Interface.PrivateKey:
            keypair = gen_keypair()
            ifdata.Interface.PrivateKey = keypair.private
            ifdata.Peer.PublicKey = keypair.public
        # Create Interface DNS config
        if not ifdata.Interface.DNS:
            if cfgdata.Dynamic.DNS:
                ifdata.Interface.DNS = ",".join(str(ip) for ip in cfgdata.Dynamic.DNS)

    raw_cfgdata = cfgdata.model_dump(mode='json', exclude_none=True)
    # pprint(raw_cfgdata)
    (OUTDIR / 'result.yaml').write_text(yaml.dump(raw_cfgdata))

    # This gets us a list of tuples with unique machine combinations. For example:
    # [(Router, Client1), (Router, Client2), (Client1, Client2)]
    unique_machine_pairs = list(combinations(cfgdata.Machines.keys(), 2))

    # After we get the unique pairing list, we can then build a dict with a distinct PSK per unique pair. Example:
    # { (Router, Client1): "psk1...", (Router, Client2): "psk2...", (Client1, Client2): "psk3..."}
    machine_pairs_psk = {pair: gen_psk() for pair in unique_machine_pairs}

    for ifname in cfgdata.Machines.keys():
        wgconf = parse_to_wg_config(ifname, cfgdata, machine_pairs_psk)
        ini = wg_config_to_ini(ifname, wgconf)
        (OUTDIR / ifname).with_suffix('.conf').write_text(ini)
