from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.core.security import decode_access_token

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

class AuthMiddleware:
    async def __call__(self, request: Request, call_next):
        if request.url.path in ["/api/register", "/api/login", "/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return await call_next(request)
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return await call_next(request)
            
            payload = decode_access_token(token)
            if payload:
                request.state.user = payload.get("sub")
        except:
            pass
        
        return await call_next(request)