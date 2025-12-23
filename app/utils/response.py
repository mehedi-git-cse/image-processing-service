import time
from typing import Any

def make_response(
    data: Any = None,
    msg: str = "",
    response_type: str = "",
    status_code: int = 200,
    response: str = "success"
):
    return {
        "responseTime": int(time.time()),
        "responseType": response_type,
        "status": status_code,
        "response": response,
        "msg": msg,
        "data": data
    }

def success(
    data: Any = None,
    msg: str = "Request successful",
    response_type: str = "",
    status_code: int = 200
):
    return make_response(
        data=data,
        msg=msg,
        response_type=response_type,
        status_code=status_code,
        response="success"
    )

def error(
    msg: str = "Something went wrong",
    data: Any = None,
    response_type: str = "",
    status_code: int = 400
):
    return make_response(
        data=data,
        msg=msg,
        response_type=response_type,
        status_code=status_code,
        response="error"
    )
