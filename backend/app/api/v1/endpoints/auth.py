from fastapi import APIRouter, Request, status
from app.core.deps import DBSession
from app.core.limiter import limiter
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, body: RegisterRequest, db: DBSession):
    return await AuthService(db).register(body.email, body.password, body.full_name)


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, db: DBSession):
    return await AuthService(db).login(body.email, body.password)
