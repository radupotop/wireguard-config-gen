from ipaddress import IPv4Interface

from pydantic import BaseModel


class Keypair(BaseModel):
    """
    A private-public keypair.
    """

    public: str
    private: str


class InterfaceModel(BaseModel):
    Address: IPv4Interface
    PrivateKey: str | None = None
    ListenPort: int | None = None


class PeerModel(BaseModel):
    AllowedIPs: list[IPv4Interface]
    ## AllowedIPs: 0.0.0.0/0, ::/0 # Forward all traffic through this server
    PublicKey: str | None = None
    Endpoint: str | None = None
    PersistentKeepalive: int | None = None


class HostModel(BaseModel):
    Interface: InterfaceModel
    Peer: PeerModel | None = None


class YamlConfig(BaseModel):
    Machines: dict[str, HostModel]
