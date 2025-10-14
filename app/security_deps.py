# общая зависимость в каждом роутере (вверху файла роутера)
from typing import Optional

from fastapi import Header, HTTPException


def require_user_id(x_user_id: Optional[int] = Header(default=None, alias="X-User-Id")) -> int:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id required")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="X-User-Id must be integer")
