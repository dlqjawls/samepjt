from sqlmodel import select, Session
from app.models.video_storage import VideoStorage
from typing import Union, List

def get_video_storage_by_id(session: Session, video_id: int) -> Union[VideoStorage, None]:
    statement = select(VideoStorage).where(VideoStorage.videoId == video_id)
    return session.exec(statement).first()

def get_all_video_storages(session: Session) -> List[VideoStorage]:
    statement = select(VideoStorage)
    return list(session.exec(statement).all())

def create_video_storage(session: Session, video_data: VideoStorage) -> VideoStorage:
    session.add(video_data)
    session.commit()
    session.refresh(video_data)
    return video_data

def update_video_storage(session: Session, video: VideoStorage) -> VideoStorage:
    session.add(video)
    session.commit()
    session.refresh(video)
    return video

def delete_video_storage(session: Session, video: VideoStorage) -> None:
    session.delete(video)
    session.commit()