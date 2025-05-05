import enum

class ResourceType(str, enum.Enum):
    VM = "VM"
    STORAGE = "STORAGE"
    SERVICE = "SERVICE"
