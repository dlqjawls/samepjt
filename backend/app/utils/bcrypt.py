import bcrypt

def hash_password(password: str) -> str:
    """
    주어진 비밀번호를 `bcrypt`로 해싱하는 함수

    Args:
        password (str): 원본 비밀번호

    Returns:
        str: 해싱된 비밀번호
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    입력된 비밀번호가 저장된 해시와 일치하는지 검증하는 함수

    Args:
        plain_password (str): 입력된 원본 비밀번호
        hashed_password (str): 데이터베이스에 저장된 해싱된 비밀번호

    Returns:
        bool: 비밀번호 일치 여부
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
