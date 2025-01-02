from datetime import UTC, datetime
from functools import cache

from models import WireguardConfig, YamlConfig


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
