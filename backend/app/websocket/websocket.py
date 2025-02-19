# Python
import json
import os
import time
import base64
import asyncio
from enum import Enum
from io import BytesIO
from typing import Dict, Any

from app.core import s3_storage

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from app.core.redis import redis_handler
from app.services.video_service import VideoService
from app.core.database import get_session
from app.utils.lut_constants import VideoType

router = APIRouter(prefix="/socket")

class MessageType(Enum):
    SERVICE = "service"
    TOPIC = "topic"

class ServiceType(Enum):
    CONNECT_VEHICLE = "/vehicle/connect"          # 차량 연결
    RENT_REQUEST = "/vehicle/rent"                # 렌트 요청
    UPDATE_DESTINATION = "/vehicle/destination/update"  # 목적지 업데이트
    RETURN = "/vehicle/return"                    # 렌트 종료
    MODULE_MOUNT = "/vehicle/module/mount"        # 모듈 장착 영상
    MODULE_RETURN = "/vehicle/module/return"      # 모듈 반납 영상

class TopicType(Enum):
    VEHICLE_STATUS = "/vehicle/status"            # 차량 상태

# 연결 관리 클래스
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.vehicle_statuses: Dict[str, Dict[str, Any]] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.vehicle_statuses[client_id] = {"connected": True, "status": "IDLE"}

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        self.vehicle_statuses.pop(client_id, None)

    async def send_personal_message(self, message: dict, client_id: str):
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_text(json.dumps(message))

    async def broadcast_topic(self, topic: str, message: dict):
        formatted_message = {
            "type": "topic",
            "path": topic,
            "payload": message
        }
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(formatted_message))

manager = ConnectionManager()

# 서비스 핸들러 함수
async def handle_connect_vehicle(client_id: str, payload: dict) -> dict:
    try:
        redis_handler.set(f"vehicle:{client_id}", "connected")
    except Exception as e:
        return {"success": False, "message": f"Redis 저장 실패: {str(e)}"}
    
    manager.vehicle_statuses[client_id]["connected"] = True
    return {"success": True, "message": "Vehicle connected successfully", "vehicle_id": client_id}

async def handle_rent_request(client_id: str, payload: dict) -> dict:
    if not manager.vehicle_statuses.get(client_id, {}).get("connected", False):
        return {"success": False, "message": "Vehicle not connected"}
    
    manager.vehicle_statuses[client_id]["status"] = "RENTED"
    return {"success": True, "message": "Rent request processed", "destination": payload.get("destination")}

async def handle_module_mount(client_id: str, payload: dict) -> dict:
    rent_id = payload.get("rent_id")
    video_content = payload.get("video")
    if not rent_id or not video_content:
        return {"success": False, "message": "rent_id 또는 video 데이터가 누락되었습니다."}
    
    # 파일 이름 생성 (예: module_mount_1676582345.mp4)
    filename = f"module_mount_{int(time.time())}.mp4"
    
    try:
        decoded_video = base64.b64decode(video_content)
        video_file_obj = BytesIO(decoded_video)
        video_url = s3_storage.upload_file_generic(
            video_file_obj, "videos/mount", rent_id, filename=filename, default_ext=".mp4",
            ExtraArgs={"ACL": "public-read", "ContentType": "video/mp4"}
        )
    except Exception as e:
        return {"success": False, "message": f"영상 업로드 실패: {str(e)}"}
      
    session = next(get_session())
    VideoService.store_video(session=session, rent_id=rent_id, video_type_id=VideoType.MODULE.ID, video_url=video_url)
    
    print(f"영상 저장 완료: {video_url}")
    return {"success": True, "message": "Module mount video processed successfully", "video_url": video_url}
  
  
async def handle_module_return(client_id: str, payload: dict) -> dict:
    rent_id = payload.get("rent_id")
    video_content = payload.get("video")
    if not rent_id or not video_content:
        return {"success": False, "message": "rent_id 또는 video 데이터가 누락되었습니다."}
    
    # 파일 이름 생성 (예: module_mount_1676582345.mp4)
    filename = f"module_return_{int(time.time())}.mp4"
    
    try:
        decoded_video = base64.b64decode(video_content)
        video_file_obj = BytesIO(decoded_video)
        video_url = s3_storage.upload_file_generic(
            video_file_obj, "videos/return", rent_id, filename=filename, default_ext=".mp4",
            ExtraArgs={"ACL": "public-read", "ContentType": "video/mp4"}
        )
    except Exception as e:
        return {"success": False, "message": f"영상 업로드 실패: {str(e)}"}
      
    session = next(get_session())
    VideoService.store_video(session = session,rent_id= rent_id,video_type_id=VideoType.AUTONOMOUS_DRIVING.ID, video_url=video_url)
    
    print(f"영상 저장 완료: {video_url}")
    return {"success": True, "message": "Module return video processed successfully", "video_url": video_url}

service_handlers = {
    ServiceType.CONNECT_VEHICLE.value: handle_connect_vehicle,
    ServiceType.RENT_REQUEST.value: handle_rent_request,
    ServiceType.MODULE_MOUNT.value: handle_module_mount,
    ServiceType.MODULE_RETURN.value: handle_module_return
}

async def process_message(client_id: str, message: dict) -> dict:
    message_type = message.get("type")
    path = message.get("path")
    payload = message.get("payload", {})

    if message_type == MessageType.SERVICE.value:
        handler = service_handlers.get(path)
        if handler:
            response = await handler(client_id, payload)
            return {"type": "service_response", "path": path, "payload": response}
        return {"type": "error", "payload": {"message": f"Unknown service: {path}"}}
    
    if message_type == MessageType.TOPIC.value:
        await manager.broadcast_topic(path, payload)
        return None
    
    return {"type": "error", "payload": {"message": "Invalid message type"}}

@router.get("/", response_class=HTMLResponse)
async def get_chat():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                print(f"Received message from {client_id}: {message}")
                response = await process_message(client_id, message)
                if response:
                    await manager.send_personal_message(response, client_id)
            except json.JSONDecodeError:
                error_msg = {"type": "error", "payload": {"message": "Invalid JSON message"}}
                await manager.send_personal_message(error_msg, client_id)
            except Exception as e:
                # 개별 메시지 처리시 발생한 기타 예외를 catch하여 연결이 끊어지지 않도록 함
                error_msg = {"type": "error", "payload": {"message": f"처리 중 오류 발생: {str(e)}"}}
                await manager.send_personal_message(error_msg, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        try:
            redis_handler.delete(f"vehicle:{client_id}")
        except Exception as e:
            print(f"Redis 삭제 실패: {e}")
        await manager.broadcast_topic(
            TopicType.VEHICLE_STATUS.value,
            {"vehicle_id": client_id, "status": "disconnected"}
        )

# WebSocketService 클래스 - 외부 모듈에서 await 없이 호출할 수 있도록 trigger 메서드 제공
class WebSocketService:
  
    @staticmethod
    async def send_rent_request_message(vin: str, rent_id: int, module_nfc_tag) -> None:
        message = {
            "type": "service",
            "path": ServiceType.RENT_REQUEST.value,
            "payload": {"rent_id": rent_id, "module_nfc_tag": module_nfc_tag}
        }
        await manager.send_personal_message(message, vin)

    @staticmethod
    def trigger_send_rent_request_message(vin: str, rent_id: int, module_nfc_tag) -> None:
        asyncio.create_task(WebSocketService.send_rent_request_message(vin, rent_id, module_nfc_tag))

    @staticmethod
    async def send_return_message(vin: str, rent_id: int, module_nfc_tag) -> None:
        message = {
            "type": "service",
            "path": ServiceType.RETURN.value,
            "payload": {"rent_id": rent_id, "module_nfc_tag": module_nfc_tag}
        }
        await manager.send_personal_message(message, vin)

    @staticmethod
    def trigger_send_return_message(vin: str, rent_id: int, module_nfc_tag) -> None:
        asyncio.create_task(WebSocketService.send_return_message(vin, rent_id, module_nfc_tag))