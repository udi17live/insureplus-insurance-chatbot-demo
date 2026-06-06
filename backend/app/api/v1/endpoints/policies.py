import uuid
from fastapi import APIRouter
from app.core.deps import CurrentUser, DBSession
from app.schemas.policy import PolicyOut
from app.services.policy import PolicyService

router = APIRouter()


@router.get("", response_model=list[PolicyOut])
async def list_policies(current_user: CurrentUser, db: DBSession):
    return await PolicyService(db).get_user_policies(current_user.id)


@router.get("/{policy_id}", response_model=PolicyOut)
async def get_policy(policy_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    return await PolicyService(db).get_policy(policy_id, current_user.id)


@router.post("/{policy_id}/cancel", response_model=PolicyOut)
async def cancel_policy(policy_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    return await PolicyService(db).cancel_policy(policy_id, current_user.id)
