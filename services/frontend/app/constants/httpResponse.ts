export const HTTP_200_OK = 200;
export const HTTP_401_UNAUTHORIZED = 401;
export const HTTP_404_NOT_FOUND = 404;
export const HTTP_408_REQUEST_TIMEOUT = 408;
export const HTTP_500_INTERNAL_SERVER_ERROR = 500;
export const HTTP_400_BAD_REQUEST = 400
export const HTTP_429_TOO_MANY_REQUESTS = 429

export const HTTP_RESPONSE_CODE = {
  [HTTP_401_UNAUTHORIZED]: {
    EMAIL_NOT_EXISTS: "email_not_exists",
    EMAIL_ALREADY_EXISTS: "email_already_exists",
    INVALID_USERNAME_OR_PASSWORD: "invalid_username_or_password",
    TOKEN_EXPIRED: "token_expired",
    INVALID_VERIFY_EMAIL_TOKEN: "invalid_verify_email_token",
    EMAIL_VERIFY_TOKEN_EXPIRED: "verify_email_token_expired",
    EMAIL_NOT_VERIFIED: "email_not_verified",
    REFRESH_TOKEN_EXPIRED: "refresh_token_expired",
    RESET_PASSWORD_TOKEN_EXPIRED: "reset_password_token_expired",
    INVALID_REFRESH_TOKEN: "invalid_refresh_token",
    INVALID_RESET_PASSWORD_TOKEN: "invalid_reset_password_token",
    AUTHENTICATION_FAILED: "keycloak_authentication_error",
    INVALID_HEADER: "invalid_header",
    DISABLED_ACCOUNT: "disabled_account",
    KEYCLOAK_USER_NOT_FOUND: "keycloak_user_not_found",
  },
  [HTTP_500_INTERNAL_SERVER_ERROR]: {
    KEYCLOAK_AUTHENTICATION_ERROR: "keycloak_authentication_error",
    INTERNAL_SERVER_ERROR: "internal_server_error",
    CONNECTION_ERROR: "connection_error",
    KEYCLOAK_ERROR: "keycloak_error",
    ARENA_STREAM_ERROR: "arena_stream_error",
    CHAT_STREAM_ERROR: "chat_stream_error",
    KEYCLOAK_SERVER_ERROR: "keycloak_server_error"
  },
  [HTTP_408_REQUEST_TIMEOUT]: {
    REQUEST_TIMEOUT: "request_timeout",
  },
  [HTTP_404_NOT_FOUND]: {
    EMAIL_NOT_EXISTS: "email_not_exists",
    NOT_FOUND: "not_found"
  }
};
