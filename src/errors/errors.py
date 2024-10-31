class ApiError(Exception):
    code = 422
    description = "Default message"

class InvalidParams(ApiError):
    code = 400
    description = "Invalid parameters"

class UserAlreadyExists(ApiError):
    code = 412
    description = "User already exists"

class InvalidToken(ApiError):
    code = 401
    description = "The token is invalid or expired."

class UserNotVerified(ApiError):
    code = 401
    description = "The user is not verified."

class HeaderInvalidToken(ApiError):
    code = 403
    description = "The token is not in the request header."

class UserNotFound(ApiError):
    code = 404
    description = "User not found"

class UserPasswordError(ApiError):
    code = 404
    description = "User password not found"


class TokenExpired(ApiError):
    code = 404
    description = "Token expired. Please log in again."


class MissingTokenError(ApiError):
    code = 403
    description = "Token is missing. Please log in again."

class JwtErrorUnknown(ApiError):
    code = 500