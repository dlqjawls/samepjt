from app.db.models.video_storage import VideoStorage
from app.db.crud.base import CRUDBase
from app.utils.exceptions import NotFoundError
from app.utils.lut_constants import LUTConstants
from app.utils.lut_constants import VideoType

class VideoStorageCRUD(CRUDBase[VideoStorage]):
    def __init__(self):
        super().__init__(VideoStorage)
    
    def get_video_type_name(self, video_type_id: int) -> str:
        """
        주어진 비디오 유형 ID에 해당하는 이름을 반환합니다.

        Args:
            video_type_id (int): 비디오 유형 ID.

        Returns:
            str: 비디오 유형 이름.

        Raises:
            NotFoundError: 비디오 유형 ID가 유효하지 않은 경우.
        """
        video_type = VideoType(video_type_id)
        mapping = LUTConstants.VIDEO_TYPE_NAMES
        video_type_name = mapping.get(video_type)

        if video_type_name is None:
            raise NotFoundError(f"Video type with ID {video_type_id} not found.")

        return video_type_name

video_storage_crud = VideoStorageCRUD()
