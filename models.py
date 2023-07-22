from pydantic import BaseModel


class InterfaceModel(BaseModel):
    Address: str
    ListenPort: int
    PrivateKey: str


class PeerModel(BaseModel):
    AllowedIPs: str
    ## AllowedIPs: 0.0.0.0/0, ::/0 # Forward all traffic through this server
    Endpoint: str | None
    PersistentKeepalive: int | None
    PublicKey: str
    PresharedKey: str


class HostModel(BaseModel):
    Interface: InterfaceModel
    Peer: PeerModel
