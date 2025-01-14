from ipaddress import IPv4Address, IPv4Interface

from pydantic import BaseModel


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
    Machines: dict[str, HostModel]
    PresharedKeyPairs: dict[str, str] = dict()
    UseUniversalPSK: bool = False


class WireguardConfig(BaseModel):
    Interface: InterfaceModel
    Peers: dict[str, PeerModel] = dict()
