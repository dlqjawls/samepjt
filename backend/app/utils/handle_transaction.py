from functools import wraps
from sqlmodel import Session
from typing import Callable, TypeVar, Any
from app.utils.exceptions import DatabaseError, ValidationError
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar("T")

def handle_transaction(func: Callable[..., T]) -> Callable[..., T]:
    """ SQLAlchemy 세션 트랜잭션 관리 데코레이터 """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        session: Session = kwargs.get("session") or args[0]
        if not session:
            if not args:
                raise DatabaseError(
                    message="No session provided",
                    detail={"function": func.__name__}
                )
            session = args[0]
            if not isinstance(session, Session):
                raise DatabaseError(
                    message="First argument must be Session",
                    detail={
                        "function": func.__name__,
                        "argument_type": type(session).__name__
                    }
                )
        try:
            result = func(*args, **kwargs)  # 함수 실행
            session.commit()  # 트랜잭션 커밋
            return result

        except SQLAlchemyError as db_err:
            # SQLAlchemy 관련 예외 처리
            session.rollback()
            raise DatabaseError(
                message="Database commit error",
                detail={"origin": str(db_err)}
            ) from db_err

          
        except Exception as e:
            session.rollback()  
            raise e
    return wrapper
