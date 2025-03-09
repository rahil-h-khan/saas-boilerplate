from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jwt_utils import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Security(oauth2_scheme)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

def check_role(required_role: str):
    def role_verification(user: dict = Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient permissions")
        return user
    return role_verification