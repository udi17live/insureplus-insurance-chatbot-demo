import uuid
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.core.deps import CurrentUser, OptionalUser, DBSession
from app.core.limiter import limiter
from app.schemas.chat import ChatMessageRequest, ThreadOut
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
            thread_id=body.thread_id,
            user_id=user_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/threads", response_model=list[ThreadOut])
async def list_threads(current_user: CurrentUser, db: DBSession):
    return await ChatService(db).list_threads(current_user.id)


@router.get("/threads/{thread_id}/messages")
async def get_thread_messages(
    thread_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    return await ChatService(db).get_thread_messages(thread_id, current_user.id)
