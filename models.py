from ipaddress import IPv4Network

from pydantic import BaseModel


class Keypair(BaseModel):
    public: str
    private: str


class InterfaceModel(BaseModel):
    Address: IPv4Network
    PrivateKey: str | None = None
    ListenPort: int | None = None


class PeerModel(BaseModel):
    AllowedIPs: list[IPv4Network]
    ## AllowedIPs: 0.0.0.0/0, ::/0 # Forward all traffic through this server
    PublicKey: str | None = None
    Endpoint: str | None = None
    PersistentKeepalive: int | None = None


class HostModel(BaseModel):
    Interface: InterfaceModel | None
    Peer: PeerModel | None
