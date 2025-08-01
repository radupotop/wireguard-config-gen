from ipaddress import IPv4Interface
from itertools import combinations
from typing import TextIO

import yaml
from genkeys import gen_keypair, gen_psk
from models import InterfaceModel, PeerModel, YamlConfig
from parsewgconfig import UNIPSK, parse_to_wg_config, wg_config_to_ini
from utils import parse_version


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


def initial_parse_yaml_config(yaml_contents: dict) -> YamlConfig:
    """
    Do minimal amounts of parsing before populating the YAML config model.
    """
    cfgdata = YamlConfig.model_validate(yaml_contents)
    cfgdata.Version = parse_version()
    cfgdata.Outdir.mkdir(exist_ok=True)
    return cfgdata


def populate_yaml_config(cfgdata: YamlConfig):
    """
    Fully populate the YAML config model.
    """
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

    if cfgdata.UseUniversalPSK:
        if UNIPSK not in cfgdata.PresharedKeyPairs:
            cfgdata.PresharedKeyPairs[UNIPSK] = gen_psk()
    else:
        # This gets us a list of strings with unique machine combinations.
        # Each pair is sorted alphabetically. For example:
        # ["Client1,Router", "Client2,Router", "Client1,Client2"]
        unique_machine_pairs = map(
            ','.join, combinations(sorted(cfgdata.Machines.keys()), 2)
        )

        for pair in unique_machine_pairs:
            if pair not in cfgdata.PresharedKeyPairs:
                cfgdata.PresharedKeyPairs[pair] = gen_psk()

    raw_cfgdata = cfgdata.model_dump(mode='json', exclude_none=True)
    # pprint(raw_cfgdata)
    outdir = cfgdata.Outdir
    (outdir / 'result.yaml').write_text(yaml.dump(raw_cfgdata))

    for ifname in cfgdata.Machines.keys():
        wgconf = parse_to_wg_config(ifname, cfgdata)
        ini = wg_config_to_ini(ifname, wgconf)
        (outdir / ifname).with_suffix('.conf').write_text(ini)

    print('Wrote to dir:')
    print(outdir.resolve())
