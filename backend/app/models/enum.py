from sqlalchemy import Enum

class AdminRole(str, Enum):
    ADMIN = "ADMIN"
    SEMI = "SEMI"

class ItemStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"

class MaintenanceStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"

class RentStatus(str, Enum):
    RESERVED = "RESERVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"

class VideoType(str, Enum):
    MODULE_INSTALLATION = "MODULE_INSTALLATION"
    AUTONOMOUS_DRIVING = "AUTONOMOUS_DRIVING"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"