from typing import Callable

import requests
import fastapi
from jose import jwt

import config


UserID = str


def validate_token(token: str) -> UserID:
    jwks = requests.get(f"{config.AUTH0_ISSUER}.well-known/jwks.json").json()
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError as exc:
        raise fastapi.HTTPException(401, "Likely malformed JWKS token") from exc

    key = {key["kid"]: key for key in jwks["keys"]}.get(unverified_header["kid"])

    if not key:
        raise fastapi.HTTPException(401, "Key from token not known")

    rsa_key = {
        "kty": key["kty"],
        "kid": key["kid"],
        "use": key["use"],
        "n": key["n"],
        "e": key["e"],
    }
    try:
        payload = jwt.decode(
            token, rsa_key, algorithms=config.AUTH0_ALGORITHMS, audience=config.AUTH0_AUDIENCE, issuer=config.AUTH0_ISSUER
        )
    except jwt.ExpiredSignatureError as exc:
        raise fastapi.HTTPException(401, "Token expired") from exc
    except jwt.JWTClaimsError as exc:
        raise fastapi.HTTPException(401, "Incorrect claims") from exc
    except Exception as exc:
        raise fastapi.HTTPException(
            401, "Unable to parse authentication token"
        ) from exc

    return payload["sub"]
