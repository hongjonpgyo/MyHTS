from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from fastapi.security import HTTPBearer
from backend_ls.app.core.jwt import SECRET_KEY, ALGORITHM

security = HTTPBearer()

def get_current_admin(credentials=Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") not in ["admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Not admin")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")