from fastapi import HTTPException, Request, status
from fastapi.routing import APIRoute
from fastapi.responses import Response
from typing import Callable

import json
import jwt
import requests


from app.core.config import settings


class AuthenticatedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            jwt_token = request.headers.get("authorization", None)

            if not jwt_token:
                raise HTTPException(
                    detail={
                        "code": "invalid_header",
                        "description": "Authorization header is not found.",
                    },
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            jwt_token_parts = jwt_token.split()
            if jwt_token_parts[0].lower() != "bearer":
                raise HTTPException(
                    detail={
                        "code": "invalid_header",
                        "description": 'Authorization header must start with "Bearer".',
                    },
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            elif len(jwt_token_parts) == 1:
                raise HTTPException(
                    detail={
                        "code": "invalid_header",
                        "description": "Token not found.",
                    },
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            elif len(jwt_token_parts) > 2:
                raise HTTPException(
                    detail={
                        "code": "invalid_header",
                        "description": 'Authorization header must be "Bearer token".',
                    },
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            token = jwt_token_parts[1]

            jwt_header = None
            try:
                jwt_header = jwt.get_unverified_header(token)
            except jwt.DecodeError:
                raise HTTPException(
                    detail={
                        "code": "invalid_header",
                        "description": "Invalid header. Use an RS256 signed JWT Access Token.",
                    },
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            except Exception as e:
                raise e

            if jwt_header["alg"] != "RS256":
                raise HTTPException(
                    detail={
                        "code": "invalid_header",
                        "description": "Invalid header. Use an RS256 signed JWT Access Token.",
                    },
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            return await original_route_handler(request)

        return custom_route_handler
