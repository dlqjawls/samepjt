# LUT 값을 상수로 미리 정의

ROLE_MAPPING = {
    1: "master",
    2: "semi",
    3: "user"
}

ITEM_STATUS_MAPPING = {
    1: "active",
    2: "inactive",
    3: "maintenance"
}

ITEM_TYPE_MAPPING = {
    1: "vehicle",
    2: "module",
    3: "option"
}

MODULE_TYPE_MAPPING = {
    1: {"name": "small", "size": "S", "cost": 100.0},
    2: {"name": "medium", "size": "M", "cost": 200.0},
    3: {"name": "large", "size": "L", "cost": 300.0}
}

MAINTENANCE_STATUS_MAPPING = {
    1: "pending",
    2: "in_progress",
    3: "completed"
}

USAGE_STATUS_MAPPING = {
    1: "in_use",
    2: "completed"
}

RENT_STATUS_MAPPING = {
    1: "in_progress",
    2: "completed",
    3: "canceled"
}

VIDEO_TYPE_MAPPING = {
    1: "module",
    2: "autonomous driving"
}

PAYMENT_STATUS_MAPPING = {
    1: "pending",
    2: "completed",
    3: "failed",
    4: "refunded"
}

PAYMENT_METHOD_MAPPING = {
    1: "credit_card",
    2: "bank_transfer",
    3: "paypal"
} 