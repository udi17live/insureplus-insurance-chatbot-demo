import uuid
from fastapi import APIRouter
from app.core.deps import CurrentUser, DBSession
from app.schemas.payment import CreatePaymentIntentRequest, PaymentIntentResponse, PaymentOut
from app.services.payment import PaymentService

router = APIRouter()


@router.post("/intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    body: CreatePaymentIntentRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    return await PaymentService(db).create_payment_intent(
        uuid.UUID(body.quote_id), current_user.id, body.currency
    )


@router.get("", response_model=list[PaymentOut])
async def list_payments(current_user: CurrentUser, db: DBSession):
    return await PaymentService(db).get_user_payments(current_user.id)
