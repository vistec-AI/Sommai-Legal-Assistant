from typing import Any

from fastapi import APIRouter

from app import schemas

router = APIRouter()


@router.get("/", response_model=schemas.Msg)
def get_health() -> Any:
    """
    Get health.

    *Example:*
    ```sh
    curl --location 'http://HOSTNAME/v1'
    ```

    """
    return schemas.Msg(msg="Service is running and healthy")
