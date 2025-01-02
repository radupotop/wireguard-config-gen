import itertools
from datetime import UTC, datetime
from functools import cache
from ipaddress import IPv4Interface
from pathlib import Path
from pprint import pprint

import yaml
from genkeys import gen_keypair, gen_psk
from models import InterfaceModel, PeerModel, WireguardConfig, YamlConfig
from yaml.loader import SafeLoader

OUTDIR = Path('output/')


@cache
def now():
    return str(datetime.now(UTC))


def parse_to_wg_config(main_ifname: str, cfgdata: YamlConfig) -> WireguardConfig:
    wgconf = WireguardConfig(
        Interface=cfgdata.Machines[main_ifname].Interface,
    )

    for ifname, ifdata in cfgdata.Machines.items():
        if ifname != main_ifname:
            wgconf.Peers[ifname] = ifdata.Peer

    # pprint(wgconf.model_dump(mode='json', exclude_none=True))
    return wgconf


def wg_config_to_ini(main_ifname: str, wgconfig: WireguardConfig) -> str:
    """
    This is not ideal but ConfigParser has too many limitations. e.g.:
      * Can't have multiple [Peer] sections with the same name
      * Comments are badly formatted
      * Can't have custom comments outside of a section
      * Keys are cast to lowercase by default
    """
    sep = '\n'
    comment = '## '
    equals = ' = '
    output = comment + 'Generated ' + now() + sep + sep

    # Add Interface section
    output += '[Interface]' + sep
    output += comment + main_ifname + sep
    for key, val in wgconfig.Interface:
        if val:
            output += key + equals + str(val) + sep
    output += sep

    # Add Peer sections
    for ifname, peer in wgconfig.Peers.items():
        output += '[Peer]' + sep
        output += comment + ifname + sep
        for key, val in peer:
            if val:
                _val = ', '.join(map(str, val)) if isinstance(val, list) else str(val)
                output += key + equals + _val + sep
        output += sep

    print(output)
    return output


def loadyaml(filepath: str):
    """
    Load a YAML file.
    """
    yaml_file = Path(filepath)
    return yaml.load(yaml_file.read_bytes(), Loader=SafeLoader)


def parseyaml(filepath: str):
    yaml_contents = loadyaml(filepath)
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


parseyaml('interfaces.yaml')
