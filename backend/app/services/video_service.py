from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select

from app.db.models.video_storage import VideoStorage
from app.utils.exceptions import NotFoundError, ValidationError

class VideoService:
    @staticmethod
    def store_video(
        session: Session,
        rent_id: int,
        video_type_id: int,
        video_url: str
    ) -> VideoStorage:
        """Store video information in the database"""
        video = VideoStorage(
            rent_id=rent_id,
            video_type_id=video_type_id,
            video_url=video_url,
            created_at=datetime.now()
        )
        session.add(video)
        session.commit()
        session.refresh(video)
        return video

    @staticmethod
    def get_videos_by_rent_id(
        session: Session,
        rent_id: int
    ) -> List[VideoStorage]:
        """Retrieve all videos associated with a rent_id"""
        videos = session.exec(
            select(VideoStorage).where(VideoStorage.rent_id == rent_id)
        ).all()
        return videos

    @staticmethod
    def get_video_by_id(
        session: Session,
        video_id: int
    ) -> Optional[VideoStorage]:
        """Retrieve a specific video by its ID"""
        video = session.get(VideoStorage, video_id)
        if not video:
            raise NotFoundError(
                message="Video not found",
                detail={"video_id": video_id}
            )
        return video
