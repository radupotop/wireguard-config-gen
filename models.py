from pydantic import BaseModel


class InterfaceModel(BaseModel):
    Address: str
    Netmask: int
    ListenPort: int
    PrivateKey: str | None


class PeerModel(BaseModel):
    AllowedIPs: str
    ## AllowedIPs: 0.0.0.0/0, ::/0 # Forward all traffic through this server
    Netmask: int
    Endpoint: str | None
    Port: int
    PersistentKeepalive: int | None
    PublicKey: str | None
    PresharedKey: str | None


class HostModel(BaseModel):
    Interface: InterfaceModel | None
    Peer: PeerModel | None
