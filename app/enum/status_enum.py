import enum

class StatusEnum(str, enum.Enum):
    running = "running"
    stopped = "stopped"
    provisioning = "provisioning"
    available = "available"
    in_progress = "in_progress"
    detected = "detected"
    mitigating = "mitigating"
    mitigated = "mitigated"
