from fastapi import APIRouter, Header, Request
from app.core.deps import DBSession
from app.services.payment import PaymentService

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: DBSession,
    stripe_signature: str = Header(..., alias="stripe-signature"),
):
    payload = await request.body()
    await PaymentService(db).handle_webhook(payload, stripe_signature)
    return {"received": True}
