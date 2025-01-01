from pydantic import BaseModel


class Keypair(BaseModel):
    public: str
    private: str


class InterfaceModel(BaseModel):
    Address: str
    Netmask: int
    ListenPort: int
    PrivateKey: str | None = None


class PeerModel(BaseModel):
    AllowedIPs: str
    ## AllowedIPs: 0.0.0.0/0, ::/0 # Forward all traffic through this server
    Netmask: int
    PublicKey: str | None = None
    EndpointHost: str | None = None
    EndpointPort: int | None = None
    PersistentKeepalive: int | None = None


class HostModel(BaseModel):
    Interface: InterfaceModel | None
    Peer: PeerModel | None
