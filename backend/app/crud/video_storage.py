from app.models.video_storage import VideoStorage
from app.crud.base import CRUDBase

class VideoStorageCRUD(CRUDBase[VideoStorage]):
    def __init__(self):
        super().__init__(VideoStorage, "video_id")
    
    def get_video_type_name(self, video_type_id: int) -> str:
        """
        주어진 비디오 유형 ID에 해당하는 이름을 반환합니다.
        """
        from app.crud.lut import get_video_type_mapping
        mapping = get_video_type_mapping()
        return mapping.get(video_type_id, "Unknown")

video_storage_crud = VideoStorageCRUD()
