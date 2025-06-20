from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import os
from typing import Optional

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

class User(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # For simplicity, we're extracting user info from the token
        # In a production environment, you might want to validate against the auth service
        user_id = payload.get("user_id", 0)  # Default to 0 if not found
        full_name = payload.get("full_name")
        
        return User(id=user_id, email=email, full_name=full_name)
        
    except JWTError:
        raise credentials_exception 