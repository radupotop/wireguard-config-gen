from enum import Enum
from ipaddress import IPv4Address, IPv4Interface
from pathlib import Path

from pydantic import BaseModel

HostName = str


class TopologyType(Enum):
    """
    In mesh mode:
        Any peer can reach any other peer.
    In star mode:
        Client peers can only reach Server peers (via the public endpoint).
        Server peers can receive from any other peer.
    The default is star mode.
    """

    mesh = 'mesh'
    star = 'star'


class Keypair(BaseModel):
    """
    A private-public keypair.
    """

    public: str
    private: str


class InterfaceModel(BaseModel):
    Address: IPv4Interface | None = None
    PrivateKey: str | None = None
    ListenPort: int | None = None
    # Has to be in the Wireguard conf format. For example: "1.1.1.1, 8.8.8.8"
    DNS: str | None = None


class PeerModel(BaseModel):
    """
    The Peer model is entirely optional since it can either be deduced from the Interface
    data or get generated at runtime.
    """

    AllowedIPs: list[IPv4Interface] | None = None
    PublicKey: str | None = None
    Endpoint: str | None = None
    PersistentKeepalive: int | None = None
    PresharedKey: str | None = None


class HostModel(BaseModel):
    Interface: InterfaceModel | None = None
    Peer: PeerModel | None = None
    # Omit all peer endpoints for this server
    # This becomes a passive server which relies on its clients to connect first.
    IsPassive: bool = False


class DynamicHost(BaseModel):
    StartIP: IPv4Address
    PrefixLen: int
    DNS: list[IPv4Address] | None = None


class YamlConfig(BaseModel):
    Version: str = 'major.minor.patch'
    Outdir: Path = Path('output/')
    Dynamic: DynamicHost
    Machines: dict[HostName, HostModel]
    PresharedKeyPairs: dict[str, str] = dict()
    UseUniversalPSK: bool = False
    Topology: TopologyType = TopologyType.star


class WireguardConfig(BaseModel):
    """
    Intermediary model which is very close to the final Wireguard conf file format.
    """

    Interface: InterfaceModel
    Peers: dict[HostName, PeerModel] = dict()
