from pprint import pprint

from models import TopologyType, WireguardConfig, YamlConfig
from utils import now, parse_version

UNIPSK = '_UNIVERSAL_'


def parse_to_wg_config(machine_name: str, ymlconfig: YamlConfig) -> WireguardConfig:
    """
    Parse the initial YAML config into an intermediary model.
    """
    this_interface = ymlconfig.Machines[machine_name].Interface
    this_peer = ymlconfig.Machines[machine_name].Peer
    wgconf = WireguardConfig(Interface=this_interface)

    # Mesh topology is the default, which is many to many
    machine_items = ymlconfig.Machines.items()
    # Only include Server peers for star topology Clients
    if ymlconfig.Topology == TopologyType.star and not this_peer.Endpoint:
        machine_items = filter(lambda n: n[1].Peer.Endpoint, machine_items)

    for ifname, ifdata in machine_items:
        if ifname != machine_name:
            wgconf.Peers[ifname] = ifdata.Peer
            # PresharedKey block
            if ymlconfig.UseUniversalPSK:
                wgconf.Peers[ifname].PresharedKey = ymlconfig.PresharedKeyPairs[UNIPSK]
            else:
                wgconf.Peers[ifname].PresharedKey = ymlconfig.PresharedKeyPairs[
                    ','.join(sorted((ifname, machine_name)))
                ]

    pprint(wgconf.model_dump(mode='json', exclude_none=True))
    return wgconf


def wg_config_to_ini(machine_name: str, wgconfig: WireguardConfig) -> str:
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
    output = (comment + 'Generated: ' + now() + sep) + (
        comment + 'From Version: ' + parse_version() + sep + sep
    )

    # Add Interface section
    output += '[Interface]' + sep
    output += comment + machine_name + sep
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

    # print(output)
    return output
