from enum import Enum
from ipaddress import IPv4Address, IPv4Interface

from pydantic import BaseModel

HostName = str


class TopologyType(Enum):
    mesh = 'mesh'  # Any peer can reach any other peer
    star = 'star'  # Client peers can only reach Server peers, Server peers can receive from any Client peer


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


class DynamicHost(BaseModel):
    StartIP: IPv4Address
    PrefixLen: int
    DNS: list[IPv4Address] | None = None


class YamlConfig(BaseModel):
    Version: str = 'major.minor.patch'
    Dynamic: DynamicHost
    Machines: dict[HostName, HostModel]
    PresharedKeyPairs: dict[str, str] = dict()
    UseUniversalPSK: bool = False
    Outdir: str = 'output/'
    Topology: TopologyType = TopologyType.mesh


class WireguardConfig(BaseModel):
    """
    Intermediary model which is very close to the final Wireguard conf file format.
    """

    Interface: InterfaceModel
    Peers: dict[str, PeerModel] = dict()
