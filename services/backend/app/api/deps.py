import gc
from typing import Generator

from fastapi import Depends, Header, HTTPException, status
from keycloak import KeycloakOpenID, KeycloakAdmin, KeycloakError
from keycloak.exceptions import KeycloakConnectionError, KeycloakAuthenticationError, KeycloakInvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from app import crud, models, schemas
from app.core.config import settings
from app.db.session import engine

token_expired_description = "Token has expired."

def get_db() -> Generator:
    try:
        db = Session(engine)
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    x_visai_authenticated_user_id: str = Header(default=None),
) -> models.User:
    user = crud.user.get(db, id=x_visai_authenticated_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "not_found",
                "description": "User not found"
            }
        )
    return user


def get_or_create_current_user(
    db: Session = Depends(get_db),
    x_visai_authenticated_user_id: str = Header(default=None),
) -> models.User:
    user = crud.user.get(db, id=x_visai_authenticated_user_id)
    if not user:
        user_in = schemas.UserCreate(id=x_visai_authenticated_user_id)
        user = crud.user.create(db, obj_in=user_in)
    return user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_URL,
    client_id=settings.KEYCLOAK_CLIENT_ID,
    realm_name=settings.KEYCLOAK_REALM,
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
)

def get_user_by_token(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    try:
        user_info = keycloak_openid.introspect(token)
        if not user_info["active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "token_expired",
                    "description": token_expired_description
                }
            )

        user_email = user_info["email"]
        user = crud.user.get_by_email(db, email=user_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "not_found",
                    "description": "User not found"
                }
            )
        return user
    except KeycloakInvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "token_expired",
                "description": f"{token_expired_description}: {str(e)}"
            }
        )
    except KeycloakAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "token_expired",
                "description": f"{token_expired_description}: {str(e)}"
            }
        )
    except KeycloakConnectionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "keycloak_server_error",
                "description": "Unable to connect to Keycloak server"
            }
        )
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "token_expired",
                "description": f"{token_expired_description}: {str(e)}"
            }
        )
    except KeycloakError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "keycloak_authentication_error",
                "description": f"Authentication service error: {str(e)}"
            }
        )
    except HTTPException as http_exc:
        # Re-raise the HTTPException to avoid handling it in the general Exception block
        raise http_exc
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": "Internal server error"
            }
        )
