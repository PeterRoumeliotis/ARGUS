from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class ClientProfile:
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    def query_keys(self) -> Dict[str, Any]:
        parts = self.name.split()
        return {
            "name": self.name,
            "first": parts[0] if parts else None,
            "last": parts[-1] if parts else None,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "address": self.address,
        }

@dataclass
class BrokerResult:
    broker: str
    found: bool
    url: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    raw_snippet: Optional[str] = None

    def to_dict(self):
        return asdict(self)