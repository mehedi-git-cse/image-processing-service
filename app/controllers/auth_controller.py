from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

from app.utils.security import SECRET_KEY
from app.utils.response import success, error


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str


VALID_CLIENT = {
    "client_id": "image-8989",
    "client_secret": "atik-check-8888"
}


def generate_token(req: TokenRequest):
    try:
        # Validate client credentials
        if (
            req.client_id != VALID_CLIENT["client_id"]
            or req.client_secret != VALID_CLIENT["client_secret"]
        ):
            return error(
                msg="Invalid client credentials",
                response_type="AUTH",
                status_code=401
            )

        # Prepare JWT payload
        payload = {
            "sub": req.client_id,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }

        # Generate token
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        # Success response
        return success(
            data={
                "access_token": token,
                "token_type": "Bearer"
            },
            msg="Token generated successfully",
            response_type="AUTH"
        )

    except Exception as e:
        # Catch any unexpected error
        return error(
            msg="Token generation failed",
            data={"error": str(e)},
            response_type="AUTH",
            status_code=500
        )
