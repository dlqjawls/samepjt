from typing import Dict, ClassVar

class BaseConstant:
    _ID_TO_NAME: ClassVar[Dict[int, str]] = {}
    _NAME_TO_ID: ClassVar[Dict[str, int]] = {}

    @classmethod
    def _initialize_mappings(cls) -> None:
        """Initialize ID-NAME mappings from nested classes"""
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, type) and hasattr(attr, 'ID') and hasattr(attr, 'NAME'):
                cls._ID_TO_NAME[attr.ID] = attr.NAME
                cls._NAME_TO_ID[attr.NAME] = attr.ID

    @classmethod
    def get_name(cls, id: int) -> str:
        if not cls._ID_TO_NAME:
            cls._initialize_mappings()
        return cls._ID_TO_NAME[id]

    @classmethod
    def get_id(cls, name: str) -> int:
        if not cls._NAME_TO_ID:
            cls._initialize_mappings()
        return cls._NAME_TO_ID[name]

class Role(BaseConstant):
    _ID_TO_NAME: ClassVar[Dict[int, str]] = {}
    _NAME_TO_ID: ClassVar[Dict[str, int]] = {}
    class MASTER:
        ID = 1
        NAME = "master"
    
    class SEMI:
        ID = 2
        NAME = "semi"
    
    class USER:
        ID = 3
        NAME = "user"

class ItemType(BaseConstant):
    _ID_TO_NAME: ClassVar[Dict[int, str]] = {}
    _NAME_TO_ID: ClassVar[Dict[str, int]] = {}
    class VEHICLE:
        ID = 1
        NAME = "vehicle"
    
    class MODULE:
        ID = 2
        NAME = "module"
    
    class OPTION:
        ID = 3
        NAME = "option"

class ItemStatus(BaseConstant):
    _ID_TO_NAME: ClassVar[Dict[int, str]] = {}
    _NAME_TO_ID: ClassVar[Dict[str, int]] = {}
    class ACTIVE:
        ID = 1
        NAME = "active"
    
    class INACTIVE:
        ID = 2
        NAME = "inactive"
    
    class MAINTENANCE:
        ID = 3
        NAME = "maintenance"

class RentStatus(BaseConstant):
    _ID_TO_NAME: ClassVar[Dict[int, str]] = {}
    _NAME_TO_ID: ClassVar[Dict[str, int]] = {}
    class IN_PROGRESS:
        ID = 1
        NAME = "in_progress"
    
    class COMPLETED:
        ID = 2
        NAME = "completed"
    
    class CANCELED:
        ID = 3
        NAME = "canceled"

class ModuleType(BaseConstant):
    _ID_TO_NAME: ClassVar[Dict[int, str]] = {}
    _NAME_TO_ID: ClassVar[Dict[str, int]] = {}
    class SMALL:
        ID = 1
        NAME = "small"
        SIZE = "3x3"
        COST = 5000
    
    class MEDIUM:
        ID = 2
        NAME = "medium"
        SIZE = "4x4"
        COST = 10000
    
    class LARGE:
        ID = 3
        NAME = "large"
        SIZE = "5x5"
        COST = 15000

class MaintenanceStatus(BaseConstant):
    _ID_TO_NAME: ClassVar[Dict[int, str]] = {}
    _NAME_TO_ID: ClassVar[Dict[str, int]] = {}
    class PENDING:
        ID = 1
        NAME = "pending"
    
    class IN_PROGRESS:
        ID = 2
        NAME = "in_progress"
    
    class COMPLETED:
        ID = 3
        NAME = "completed"

class UsageStatus(BaseConstant):
    _ID_TO_NAME: ClassVar[Dict[int, str]] = {}
    _NAME_TO_ID: ClassVar[Dict[str, int]] = {}
    class IN_USE:
        ID = 1
        NAME = "in_use"
    
    class COMPLETED:
        ID = 2
        NAME = "completed"

class VideoType(BaseConstant):
    _ID_TO_NAME: ClassVar[Dict[int, str]] = {}
    _NAME_TO_ID: ClassVar[Dict[str, int]] = {}
    class MODULE:
        ID = 1
        NAME = "module"
    
    class AUTONOMOUS_DRIVING:
        ID = 2
        NAME = "autonomous_driving"

class PaymentStatus(BaseConstant):
    _ID_TO_NAME: ClassVar[Dict[int, str]] = {}
    _NAME_TO_ID: ClassVar[Dict[str, int]] = {}
    class PENDING:
        ID = 1
        NAME = "pending"
    
    class COMPLETED:
        ID = 2
        NAME = "completed"
    
    class FAILED:
        ID = 3
        NAME = "failed"
    
    class REFUNDED:
        ID = 4
        NAME = "refunded"

class PaymentMethod(BaseConstant):
    _ID_TO_NAME: ClassVar[Dict[int, str]] = {}
    _NAME_TO_ID: ClassVar[Dict[str, int]] = {}
    class CREDIT_CARD:
        ID = 1
        NAME = "credit_card"
    
    class BANK_TRANSFER:
        ID = 2
        NAME = "bank_transfer"
    
    class PAYPAL:
        ID = 3
        NAME = "paypal"