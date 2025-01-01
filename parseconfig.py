import configparser
import io
import itertools
from ipaddress import IPv4Interface
from pathlib import Path
from pprint import pprint

import yaml
from genkeys import gen_keypair, gen_psk
from models import InterfaceModel, PeerModel, WireguardConfig, YamlConfig
from yaml.loader import SafeLoader


def parse_to_wg_config(main_ifname: str, cfgdata: YamlConfig) -> WireguardConfig:
    wgconf = WireguardConfig(
        Interface=cfgdata.Machines[main_ifname].Interface,
    )

    for ifname, ifdata in cfgdata.Machines.items():
        if ifname != main_ifname:
            wgconf.Peers[ifname] = ifdata.Peer

    # pprint(wgconf.model_dump(mode='json', exclude_none=True))
    return wgconf


def wg_config_to_ini(main_ifname: str, config: WireguardConfig) -> str:
    parser = configparser.ConfigParser(allow_no_value=True)

    # Add Interface section
    parser.add_section('Interface')
    parser.set('Interface', '##', main_ifname)
    for key, value in config.Interface:
        if value:
            parser.set('Interface', key.title(), str(value))

    # Add Peer sections
    cnt = itertools.count(1)
    for ifname, peer in config.Peers.items():
        section_name = f'Peer__{next(cnt)}'
        parser.add_section(section_name)
        parser.set(section_name, '##', ifname)
        for key, value in peer:
            if isinstance(value, list):
                parser.set(section_name, key.title(), ','.join(map(str, value)))
            elif value:
                parser.set(section_name, key.title(), str(value))

    # Write to a string
    ini_file = io.StringIO()
    parser.write(ini_file)
    ini_str = ini_file.getvalue().replace('## =', '##')

    print(ini_str)

    return ini_str


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

    for ifname in cfgdata.Machines.keys():
        print(ifname)
        wgconf = parse_to_wg_config(ifname, cfgdata)
        ini = wg_config_to_ini(ifname, wgconf)


parseyaml()
