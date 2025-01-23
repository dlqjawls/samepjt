from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.video_storage import VideoStorage
from typing import Optional, List
from fastapi import HTTPException

def get_video_storage_by_id(session: Session, video_id: Optional[int]) -> Optional[VideoStorage]:
    if video_id is None:
        raise HTTPException(status_code=400, detail="Video ID cannot be None")

    statement = select(VideoStorage).where(VideoStorage.videoId == video_id)
    result = session.exec(statement).first()
    
    return result 

def get_all_video_storages(session: Session) -> List[VideoStorage]:
    return list(session.exec(select(VideoStorage)).all())

def create_video_storage(session: Session, video_data: VideoStorage) -> VideoStorage:
    try:
        session.add(video_data)
        session.commit()
        session.refresh(video_data)
        return video_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create video storage")

def update_video_storage(session: Session, video: VideoStorage) -> VideoStorage:
    existing_video = get_video_storage_by_id(session, video.videoId)
    
    if not existing_video:
        raise HTTPException(status_code=404, detail=f"Video Storage with ID {video.videoId} does not exist")
    
    session.add(video)
    session.commit()
    session.refresh(video)
    return video

def delete_video_storage(session: Session, video_id: int) -> None:
    video = get_video_storage_by_id(session, video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail=f"Video Storage with ID {video_id} does not exist")
    
    session.delete(video)
    session.commit()
