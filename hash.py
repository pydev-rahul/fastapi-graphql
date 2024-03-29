from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']     # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY'] 


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    def bcrypt(password: str):
        """
        Encrypt password as hashed password.
    
    
        Parameters:
        arg1 (string): Password string provided by user.
    
        Returns:
        String: Hased Password.
        """
        return pwd_context.hash(password)

    def verify(hashed_password, plain_password):
        """
        Verify the user by password.
    
    
        Parameters:
        arg1 (string): Hashed Password fetch from DB.
        arg2 (string): Plain text password provided by user..
    
        Returns:
        Bool: Return True if it's verify otherwise return False.
        """
        return pwd_context.verify(plain_password, hashed_password)

#########################################

def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """
        Creating access token from secrect key and provided user email.
    
    
        Parameters:
        arg1 (string or any): Provided any string or any type data by User.
        arg2 (int): Expire time entering by user.
    
        Returns:
        Sring: Return Encoded JWT Token.
    """
    expires_delta = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """
        Creating refresh token from secrect key and provided user email.
    
    
        Parameters:
        arg1 (string or any): Provided any string or any type data by User.
        arg2 (int): Expire time entering by user.
    
        Returns:
        Sring: Return Encoded JWT Token.
    """ 
    expires_delta = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt