from typing import List, TypeVar
from app.schemas.pagination import Pagination, PaginatedResponse

T = TypeVar("T")


def paginate(data: List[T], page: int, page_size: int) -> PaginatedResponse[T]:
    """
    리스트를 페이지네이션하여 반환합니다.

    - `data`: 원본 리스트
    - `page`: 현재 페이지 번호
    - `page_size`: 페이지 크기
    """
    total_items = len(data)
    total_pages = (total_items // page_size) + (1 if total_items % page_size > 0 else 0)

    # 요청한 페이지가 범위를 벗어나면 빈 리스트 반환
    if page > total_pages and total_pages != 0:
        return PaginatedResponse(items=[], pagination=Pagination(
            currentPage=page, totalPages=total_pages, totalItems=total_items, pageSize=page_size
        ))

    paginated_data = data[(page - 1) * page_size : page * page_size]

    return PaginatedResponse(
        items=paginated_data,
        pagination=Pagination(
            currentPage=page,
            totalPages=total_pages,
            totalItems=total_items,
            pageSize=page_size
        )
    )
