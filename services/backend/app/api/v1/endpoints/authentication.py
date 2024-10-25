from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Form,
    HTTPException,
    status,
    Query
)
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from typing import Any, List, Optional
from uuid import UUID
from pydantic import UUID4
import uuid
import jwt
from app import crud, models, schemas
from app.api import deps
from keycloak import KeycloakOpenID, KeycloakAdmin, KeycloakOpenIDConnection, KeycloakError
from keycloak.exceptions import KeycloakGetError, KeycloakAuthenticationError, KeycloakInvalidTokenError, KeycloakConnectionError
from app.core.config import settings
from app.models.user import User
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.api.custom_route import AuthenticatedRoute
from datetime import datetime, timedelta

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
class UserRefreshToken(BaseModel):
    refresh_token: str
class UpdateUserInfoRequest(BaseModel):
    email: str
class UserResetPassword(BaseModel):
    email: str
    new_password: str
    token: str


router = APIRouter()
auth_router = APIRouter(route_class=AuthenticatedRoute)

keycloak_admin = KeycloakAdmin(
    server_url=settings.KEYCLOAK_URL,
    username=settings.KEYCLOAK_REALM_ADMIN,
    password=settings.KEYCLOAK_REALM_ADMIN_PASSWORD,
    realm_name=settings.KEYCLOAK_REALM,
    client_id=settings.KEYCLOAK_CLIENT_ID,
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
    verify=True
)
keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_URL,
    client_id=settings.KEYCLOAK_CLIENT_ID,
    realm_name=settings.KEYCLOAK_REALM,
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
    # verify=True
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

request_reset_password_expiration = 2 * 24 * 60 * 60 # 2 days


@router.post("/register", response_model=TokenResponse)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserRequestCreate,
) -> Any:
    try:
        user = crud.user.get_by_email(db=db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "email_already_exists",
                    "description": "Email already exists"
                }
            )

        keycloak_user_id = keycloak_admin.create_user({
            "email": user_in.email,
            "username": user_in.email,
            "enabled": True,
            "credentials": [{"value": user_in.password, "type": "password", "temporary": False}]
        })
        register_in = schemas.UserCreate(email=user_in.email, keycloak_user_id=keycloak_user_id, has_accepted_terms=True)
        new_user = crud.user.create(
            db=db, obj_in=register_in
        )
        token = keycloak_openid.token(username=user_in.email, password=user_in.password, grant_type=["password"])
        # create chat room for new user
        chat_room_in =schemas.ChatRoomCreate(name="การสนทนาใหม่")
        crud.chat_room.create(db=db, obj_in=chat_room_in, user_id=new_user.id)

        return {"access_token": token['access_token'], "refresh_token": token['refresh_token']}

    except KeycloakError as e:
        error_description = str(e).lower()
        if "exists with same email" in error_description:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "email_already_exists",
                    "description": str(e)
                }
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "keycloak_error",
                "description": str(e)
            }
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": str(e)
            }
        )

@router.post("/login", response_model=TokenResponse)
def login(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserRequestCreate,
) -> Any:
    try:
        user = crud.user.get_by_email(db=db, email=user_in.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "email_not_exists",
                    "description": "Email not exists"
                }
            )
        token = keycloak_openid.token(username=user_in.email, password=user_in.password, grant_type=["password"])
        return {
            "access_token": token['access_token'],
            "refresh_token": token['refresh_token'],
        }
    except KeycloakAuthenticationError as e:
        error_description = str(e).lower()
        print('KeycloakAuthenticationError: ', error_description)
        if "invalid_grant" in error_description:
            if "invalid credentials" in error_description:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "invalid_username_or_password",
                        "description": "Invalid username or password"
                    }
                )
            elif "user is disabled" in error_description:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "disabled_account",
                        "description": "User account is disabled"
                    }
                )
            elif "invalid user credentials" in error_description:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "invalid_username_or_password",
                        "description": "Invalid username or password"
                    }
                )
        elif "user not found" in error_description:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "keycloak_user_not_found",
                    "description": "User not found"
                }
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "keycloak_authentication_error",
                "description": str(e)
            }
        )
    except KeycloakError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "keycloak_error",
                "description": str(e)
            }
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": str(e)
            }
        )

@router.post("/refresh", response_model=TokenResponse)
def refresh(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserRefreshToken,
) -> Any:
    try:
        print('-----refresh-----')
        token = keycloak_openid.refresh_token(user_in.refresh_token)
        return {
            "access_token": token["access_token"],
            "refresh_token": token["refresh_token"],
        }

    except KeycloakError as e:
        print("Refresh KeycloakError: ", e)
        if "invalid_grant" in str(e):
            if "Invalid refresh token" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "invalid_refresh_token",
                        "description": "Invalid refresh token"
                    }
                )
            elif "Refresh token expired" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "refresh_token_expired",
                        "description": "Refresh token has expired"
                    }
                )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "keycloak_authentication_error",
                "description": str(e)
            }
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "refresh_token_expired",
                "description": "Refresh token has expired"
            }
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "invalid_refresh_token",
                "description": "Invalid refresh token"
            }
        )
    except KeycloakAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "keycloak_authentication_error",
                "description": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": str(e)
            }
        )

@router.post("/logout")
def logout(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserRefreshToken,
) -> Any:
    try:
        keycloak_openid.logout(user_in.refresh_token)
        return {"detail": "User successfully logged out."}
    except KeycloakError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "keycloak_authentication_error",
                "description": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/user/accept-terms")
def update_user_accepted_terms(
     *,
    db: Session = Depends(deps.get_db),
    user_in: UpdateUserInfoRequest
) -> Any:
    try:
        user = crud.user.get_by_email(db=db, email=user_in.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "email_not_exists",
                    "description": "Email not exists"
                }
            )
        user_accepted_terms = schemas.UserUpdate(has_accepted_terms=True)
        updated_user = crud.user.update(db=db, db_obj=user, obj_in=user_accepted_terms)
        return {"detail": "Update user successfully accepted terms."}
    except KeycloakError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "keycloak_error",
                "description": str(e)
            }
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": str(e)
            }
        )


@auth_router.get("/user/email")
def get_user_email(
    db: Session = Depends(deps.get_db),
    token: str = Depends(oauth2_scheme)
) -> Any:
    try:
        user_info = keycloak_openid.introspect(token)
        if not user_info["active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "token_expired",
                    "description": "Token has expired."
                }
            )
        email = user_info['email']
        user = crud.user.get_by_email(db=db, email=email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "email_not_exists",
                    "description": "Email not exists"
                }
            )
        return {"email": user.email}

    except KeycloakInvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "token_expired",
                "description": "Token has expired."
            }
        )
    except KeycloakAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "token_expired",
                "description": "Token has expired."
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
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "token_expired",
                "description": "Token has expired."
            }
        )
    except KeycloakError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "keycloak_authentication_error",
                "description": str(e)
            }
        )
    except HTTPException as http_exc:
        # Re-raise the HTTPException to avoid handling it in the general Exception block
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": str(e)
            }
        )

@router.get("/user/is-accepted-terms")
def accept_term(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10000,
    email: str = Query(None, description="User email"),
) -> Any:
    if email is None:
        raise HTTPException(
                status_code=400,
                detail={
                    "code": "invalid_email",
                    "description": "No email provided"
                }
            )
    try:
        user = crud.user.get_by_email(db=db, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "email_not_exists",
                    "description": "Email not exists"
                }
            )
        return {"has_accepted_terms": user.has_accepted_terms}
    except KeycloakError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "keycloak_error",
                "description": str(e)
            }
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": str(e)
            }
        )

@router.post("/request-reset-password")
def request_reset_password(
     *,
    db: Session = Depends(deps.get_db),
    user_in: UpdateUserInfoRequest,
) -> Any:
    try:
        user = crud.user.get_by_email(db=db, email=user_in.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "email_not_exists",
                    "description": "Email not exists"
                }
            )
        token = str(uuid.uuid4())
        expiration = datetime.utcnow() + timedelta(days=2)

        user_token = schemas.UserUpdate(token=token, token_expiration=expiration)
        updated_user = crud.user.update(db=db, db_obj=user, obj_in=user_token)

        frontend_url = settings.FRONTEND_URL
        reset_password_link = f"{frontend_url}/auth/reset-password?email={user_in.email}&token={token}"
        return {"redirect": reset_password_link}
    except KeycloakError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "keycloak_error",
                "description": str(e)
            }
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": str(e)
            }
        )

@router.post("/reset-password")
def reset_password(
     *,
    db: Session = Depends(deps.get_db),
    user_in: UserResetPassword,
) -> Any:
    try:
        user = crud.user.get_by_email(db=db, email=user_in.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "email_not_exists",
                    "description": "Email not exists"
                }
            )


        validate_token = user_in.token == user.token
        if not validate_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "invalid_reset_password_token",
                    "description": "Reset password is invalid"
                }
            )
        if user.token_expiration < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "reset_password_token_expired",
                    "description": "Reset password token is invalid"
                }
            )

        keycloak_admin.set_user_password(user_id=user.keycloak_user_id, password=user_in.new_password, temporary=False)
        reset_user_token = schemas.UserUpdate(token=None, token_expiration=None)
        updated_user = crud.user.update(db=db, db_obj=user, obj_in=reset_user_token)

        return {"detail": "Password reset successfully"}

    except KeycloakError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "keycloak_error",
                "description": str(e)
            }
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "internal_server_error",
                "description": str(e)
            }
        )


@router.get("/listing")
def listing_user(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10000,
) -> Any:
    filtered_chats = db.query(Chat).all()

    responses = []
    for chat in filtered_chats:
        user = db.query(User).filter(User.id == chat.user_id).first()
        if user:
            responses.append(
                UsedUserModel(
                    email=user.email,
                    date=chat.created_at.strftime('%Y-%m-%d %H:%M:%S')
                )
            )
    if email:
      responses = [response for response in responses if response.email == email]
    email_map = {}
    for entry in responses:
        email = entry.email
        # Update the map to keep the latest date and total count
        if email in email_map:
            email_map[email]["date"] = entry.date
            email_map[email]["total_chat"] += 1
        else:
            email_map[email] = {
                "email": entry.email,
                "latest_date": entry.date,
                "total_chat": 1
            }
    final_result = list(email_map.values())
    sorted_result = sorted(final_result, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'))

    return sorted_result
