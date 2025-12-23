import jwt
from app.utils.response import error

SECRET_KEY = "ATIK-IMAGE_PROCESSING-SECRET"


def verify_api_key_plain(authorization: str | None):
    if not authorization:
        return error(
            msg="Authorization header missing",
            response_type="AUTH",
            status_code=401
        )

    if not authorization.startswith("Bearer "):
        return error(
            msg="Invalid token format",
            response_type="AUTH",
            status_code=401
        )

    token = authorization.replace("Bearer ", "").strip()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload  # valid token → return payload

    except jwt.ExpiredSignatureError:
        return error(
            msg="Token expired",
            response_type="AUTH",
            status_code=401
        )

    except jwt.InvalidTokenError:
        return error(
            msg="Invalid token",
            response_type="AUTH",
            status_code=401
        )

    except Exception as e:
        return error(
            msg="Authentication failed",
            data={"error": str(e)},
            response_type="AUTH",
            status_code=500
        )
