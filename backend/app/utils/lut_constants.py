# LUT 값을 상수로 미리 정의
from enum import IntEnum
from typing import Any, Dict

class Role(IntEnum):
    MASTER = 1
    SEMI = 2
    USER = 3

class ItemType(IntEnum):
    VEHICLE = 1
    MODULE = 2
    OPTION = 3

class ItemStatus(IntEnum):
    ACTIVE = 1
    INACTIVE = 2
    MAINTENANCE = 3

class RentStatus(IntEnum):
    IN_PROGRESS = 1
    COMPLETED = 2
    CANCELED = 3

class ModuleType(IntEnum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class MaintenanceStatus(IntEnum):
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETED = 3

class UsageStatus(IntEnum):
    IN_USE = 1
    COMPLETED = 2

class VideoType(IntEnum):
    MODULE = 1
    AUTONOMOUS_DRIVING = 2

class PaymentStatus(IntEnum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3
    REFUNDED = 4

class PaymentMethod(IntEnum):
    CREDIT_CARD = 1
    BANK_TRANSFER = 2
    PAYPAL = 3

class LUTConstants:
    """LUT 상수들을 관리하는 클래스입니다."""
    
    ROLE_NAMES: Dict[Role, str] = {
        Role.MASTER: "master",
        Role.SEMI: "semi",
        Role.USER: "user"
    }

    ITEM_TYPE_NAMES: Dict[ItemType, str] = {
        ItemType.VEHICLE: "vehicle",
        ItemType.MODULE: "module",
        ItemType.OPTION: "option"
    }

    ITEM_STATUS_NAMES: Dict[ItemStatus, str] = {
        ItemStatus.ACTIVE: "active",
        ItemStatus.INACTIVE: "inactive",
        ItemStatus.MAINTENANCE: "maintenance"
    }

    RENT_STATUS_NAMES: Dict[RentStatus, str] = {
        RentStatus.IN_PROGRESS: "in_progress",
        RentStatus.COMPLETED: "completed",
        RentStatus.CANCELED: "canceled"
    }

    MODULE_TYPE_INFO: Dict[ModuleType, Dict[str, Any]] = {
        ModuleType.SMALL: {"name": "small", "size": "S", "cost": 5000},
        ModuleType.MEDIUM: {"name": "medium", "size": "M", "cost": 10000},
        ModuleType.LARGE: {"name": "large", "size": "L", "cost": 15000}
    }

    MAINTENANCE_STATUS_NAMES: Dict[MaintenanceStatus, str] = {
        MaintenanceStatus.PENDING: "pending",
        MaintenanceStatus.IN_PROGRESS: "in_progress",
        MaintenanceStatus.COMPLETED: "completed"
    }

    USAGE_STATUS_NAMES: Dict[UsageStatus, str] = {
        UsageStatus.IN_USE: "in_use",
        UsageStatus.COMPLETED: "completed"
    }

    VIDEO_TYPE_NAMES: Dict[VideoType, str] = {
        VideoType.MODULE: "module",
        VideoType.AUTONOMOUS_DRIVING: "autonomous driving"
    }

    PAYMENT_STATUS_NAMES: Dict[PaymentStatus, str] = {
        PaymentStatus.PENDING: "pending",
        PaymentStatus.COMPLETED: "completed",
        PaymentStatus.FAILED: "failed",
        PaymentStatus.REFUNDED: "refunded"
    }

    PAYMENT_METHOD_NAMES: Dict[PaymentMethod, str] = {
        PaymentMethod.CREDIT_CARD: "credit_card",
        PaymentMethod.BANK_TRANSFER: "bank_transfer",
        PaymentMethod.PAYPAL: "paypal"
    } 