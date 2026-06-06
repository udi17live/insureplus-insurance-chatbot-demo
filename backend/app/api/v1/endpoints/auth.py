from fastapi import APIRouter, status
from app.core.deps import DBSession
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: DBSession):
    return await AuthService(db).register(body.email, body.password, body.full_name)


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: DBSession):
    return await AuthService(db).login(body.email, body.password)
