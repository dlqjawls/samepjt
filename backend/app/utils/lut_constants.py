# LUT 값을 상수로 미리 정의
from enum import IntEnum

class ROLE(IntEnum):
    MASTER = 1
    SEMI = 2
    USER = 3

class ITEM_TYPE(IntEnum):
    VEHICLE = 1
    MODULE = 2
    OPTION = 3

class ITEM_STATUS(IntEnum):
    ACTIVE = 1
    INACTIVE = 2
    MAINTENANCE = 3

class RENT_STATUS(IntEnum):
    IN_PROGRESS = 1
    COMPLETED = 2
    CANCELED = 3

class MODULE_TYPE(IntEnum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class MAINTENANCE_STATUS(IntEnum):
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETED = 3

class USAGE_STATUS(IntEnum):
    IN_USE = 1
    COMPLETED = 2

class VIDEO_TYPE(IntEnum):
    MODULE = 1
    AUTONOMOUS_DRIVING = 2

class PAYMENT_STATUS(IntEnum):
    PENDING = 1
    COMPLETED = 2
    FAILED = 3
    REFUNDED = 4

class PAYMENT_METHOD(IntEnum):
    CREDIT_CARD = 1
    BANK_TRANSFER = 2
    PAYPAL = 3

# 매핑 정보
ROLE_MAPPING = {
    ROLE.MASTER: "master",
    ROLE.SEMI: "semi",
    ROLE.USER: "user"
}

ITEM_TYPE_MAPPING = {
    ITEM_TYPE.VEHICLE: "vehicle",
    ITEM_TYPE.MODULE: "module",
    ITEM_TYPE.OPTION: "option"
}

ITEM_STATUS_MAPPING = {
    ITEM_STATUS.ACTIVE: "active",
    ITEM_STATUS.INACTIVE: "inactive",
    ITEM_STATUS.MAINTENANCE: "maintenance"
}

RENT_STATUS_MAPPING = {
    RENT_STATUS.IN_PROGRESS: "in_progress",
    RENT_STATUS.COMPLETED: "completed",
    RENT_STATUS.CANCELED: "canceled"
}

MODULE_TYPE_MAPPING = {
    MODULE_TYPE.SMALL: {"name": "small", "size": "S", "cost": 100.0},
    MODULE_TYPE.MEDIUM: {"name": "medium", "size": "M", "cost": 200.0},
    MODULE_TYPE.LARGE: {"name": "large", "size": "L", "cost": 300.0}
}

MAINTENANCE_STATUS_MAPPING = {
    MAINTENANCE_STATUS.PENDING: "pending",
    MAINTENANCE_STATUS.IN_PROGRESS: "in_progress",
    MAINTENANCE_STATUS.COMPLETED: "completed"
}

USAGE_STATUS_MAPPING = {
    USAGE_STATUS.IN_USE: "in_use",
    USAGE_STATUS.COMPLETED: "completed"
}

VIDEO_TYPE_MAPPING = {
    VIDEO_TYPE.MODULE: "module",
    VIDEO_TYPE.AUTONOMOUS_DRIVING: "autonomous driving"
}

PAYMENT_STATUS_MAPPING = {
    PAYMENT_STATUS.PENDING: "pending",
    PAYMENT_STATUS.COMPLETED: "completed",
    PAYMENT_STATUS.FAILED: "failed",
    PAYMENT_STATUS.REFUNDED: "refunded"
}

PAYMENT_METHOD_MAPPING = {
    PAYMENT_METHOD.CREDIT_CARD: "credit_card",
    PAYMENT_METHOD.BANK_TRANSFER: "bank_transfer",
    PAYMENT_METHOD.PAYPAL: "paypal"
} 