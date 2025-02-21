from app.db.models.video_storage import VideoStorage
from app.db.crud.base import CRUDBase
from typing import List, Optional

class VideoStorageCRUD(CRUDBase[VideoStorage]):
    def __init__(self):
        super().__init__(VideoStorage)
        
    def get_by_rent_id(self, session, rent_id: int, video_type_id: Optional[int]) -> List[VideoStorage]:
        if video_type_id is None:
            return session.query(VideoStorage).filter(VideoStorage.rent_id == rent_id).all()
        return session.query(VideoStorage).filter(VideoStorage.rent_id == rent_id, 
                                                  VideoStorage.video_type_id == video_type_id).all()

video_storage_crud = VideoStorageCRUD()
