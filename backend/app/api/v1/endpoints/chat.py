from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.core.deps import CurrentUser, OptionalUser, DBSession
from app.core.limiter import limiter
from app.schemas.chat import ChatMessageRequest, SessionOut
from app.services.chat import ChatService

router = APIRouter()


@router.post("/message")
@limiter.limit("20/minute")
async def send_message(
    request: Request,
    body: ChatMessageRequest,
    current_user: OptionalUser,
    db: DBSession,
):
    user_id = current_user.id if current_user else None
    service = ChatService(db)
    return StreamingResponse(
        service.stream_response(
            message=body.message,
            session_id=body.session_id,
            user_id=user_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sessions", response_model=list[SessionOut])
async def list_sessions(current_user: CurrentUser, db: DBSession):
    return await ChatService(db).list_sessions(current_user.id)
