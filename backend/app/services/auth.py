from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token, hash_password, verify_password
from app.repository.user import UserRepository
from app.schemas.auth import AuthResponse, UserOut


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def register(self, email: str, password: str, full_name: str | None) -> AuthResponse:
        if await self.repo.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = await self.repo.create(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
        )

        token = create_access_token(str(user.id), user.email)
        return AuthResponse(
            access_token=token,
            user=UserOut(id=str(user.id), email=user.email, full_name=user.full_name),
        )

    async def login(self, email: str, password: str) -> AuthResponse:
        user = await self.repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

        token = create_access_token(str(user.id), user.email)
        return AuthResponse(
            access_token=token,
            user=UserOut(id=str(user.id), email=user.email, full_name=user.full_name),
        )
