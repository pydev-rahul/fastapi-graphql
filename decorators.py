from jwt import encode, decode
from fastapi import status, HTTPException
import jwt
from jwt.exceptions import ExpiredSignatureError
from hash import ALGORITHM, JWT_SECRET_KEY

def authenticate(original_function):
    """
    Authenticate user before access every query and mutation.
    Authenticate via token. 
    """
    def wrapper(*args, **kwargs):
        # Get the token from the request header
        token = args[1].context.get("request").headers.get('Authorization')
        if not token :
            raise Exception("Token not provided")
        try:
            data = jwt.decode(token.split()[-1], JWT_SECRET_KEY, ALGORITHM)
            if data:
              return original_function(*args, **kwargs)
        except ExpiredSignatureError:
            raise Exception("Token is expired")
        except Exception as e:
            raise Exception("Invalid Token")
    return wrapper