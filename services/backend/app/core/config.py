from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/v1"
    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    RABBITMQ_HOST: str = ""
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USERNAME: str = ""
    RABBITMQ_PASSWORD: str = ""
    KEYCLOAK_URL: str = ""
    KEYCLOAK_REALM: str = ""
    KEYCLOAK_CLIENT_ID: str = ""
    KEYCLOAK_CLIENT_SECRET: str = ""
    KEYCLOAK_REALM_ADMIN: str = ""
    KEYCLOAK_REALM_ADMIN_PASSWORD: str = ""
    FRONTEND_URL: str = ""



settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
