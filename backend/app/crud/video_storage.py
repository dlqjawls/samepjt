from app.models.video_storage import VideoStorage
from app.crud.base import CRUDBase

class VideoStorageCRUD(CRUDBase[VideoStorage]):
    def __init__(self):
        super().__init__(VideoStorage, "video_id")
    
video_storage_crud = VideoStorageCRUD()
