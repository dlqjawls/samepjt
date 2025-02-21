import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from app.core.config import settings
import os
import uuid
from typing import Optional
from app.utils.exceptions import DatabaseError


s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)

def upload_file_to_s3(file_obj, bucket_name: str, object_name: str, ExtraArgs: dict = {"ACL": "public-read"}) -> str:
    """
    파일 객체를 아마존 S3 버킷에 업로드하고, 파일 URL을 반환합니다.

    Args:
        file_obj: 업로드할 파일 객체.
        bucket_name (str): 업로드할 S3 버킷 이름.
        object_name (str): S3 버킷 내에 저장할 파일 경로 및 파일명.

    Returns:
        str: 업로드된 파일의 URL.
    """
    try:
        s3.upload_fileobj(file_obj, bucket_name, object_name, ExtraArgs)
        # 기본적으로 S3 버킷의 public 접근 설정(정책)에 따라 URL 접근이 가능해야 합니다.
        url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        return url
    except NoCredentialsError:
        raise DatabaseError(message="AWS 자격 증명이 설정되지 않았습니다.")
    except ClientError as e:
        raise DatabaseError(message=f"S3 upload error: {e}")

def list_files_by_prefix(prefix: str) -> list:
    """
    지정된 prefix를 기준으로 S3 버킷에서 파일 목록을 조회합니다.
    파일이 없으면 빈 리스트 []를 반환합니다.
    
    Args:
        prefix (str): 객체 키의 접두사(prefix)
    
    Returns:
        list: 객체 키 리스트
    """
    try:
        response = s3.list_objects_v2(Bucket=settings.s3_bucket_name, Prefix=prefix)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []
    except ClientError as e:
        raise Exception(f"Failed to list objects: {e}")

def upload_file_generic(file_obj, *path_parts, filename: Optional[str] = None, default_ext: str = ".jpg", ExtraArgs: dict = {"ACL": "public-read"}) -> str:
    """
    일반화된 파일 업로드 함수.
    path_parts를 받아 경로를 구성하고, 파일 이름이 미지정되면 UUID 기반 이름을 생성합니다.
    
    Args:
        file_obj: 업로드할 파일 객체.
        *path_parts: 경로의 각 구성 요소들.
        filename (str, optional): 파일 이름.
        default_ext (str): 기본 확장자.
        
    Returns:
        str: 업로드된 파일의 URL.
    """
    if filename is None:
        original_filename = getattr(file_obj, "filename", None)
        ext = os.path.splitext(original_filename)[1] if (original_filename and os.path.splitext(original_filename)[1]) else default_ext
        filename = f"{uuid.uuid4()}{ext}"
    object_name = "/".join([str(part) for part in path_parts] + [filename])
    return upload_file_to_s3(file_obj, settings.s3_bucket_name, object_name, ExtraArgs)

def list_files_by_category(*path_parts) -> list:
    """
    일반화된 파일 목록 조회 함수.
    path_parts를 이용해 prefix를 구성하여 객체 목록을 조회합니다.
    
    Returns:
        list: 객체 키 리스트.
    """
    prefix = "/".join([str(part) for part in path_parts]) + "/"
    return list_files_by_prefix(prefix)