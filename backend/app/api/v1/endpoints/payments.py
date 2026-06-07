import uuid
from fastapi import APIRouter
from app.core.deps import CurrentUser, DBSession
from app.schemas.payment import ConfirmPaymentRequest, PaymentOut
from app.schemas.policy import PolicyOut
from app.services.payment import PaymentService

router = APIRouter()


@router.post("/confirm", response_model=PolicyOut)
async def confirm_payment(
    body: ConfirmPaymentRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    return await PaymentService(db).confirm_payment(uuid.UUID(body.quote_id), current_user.id)


@router.get("", response_model=list[PaymentOut])
async def list_payments(current_user: CurrentUser, db: DBSession):
    return await PaymentService(db).get_user_payments(current_user.id)
