import uuid
from fastapi import APIRouter, HTTPException, status
from app.core.deps import AgentAuth, DBSession
from app.schemas.agent import AgentQuoteCreate, AgentQuoteOut, AgentPolicyOut
from app.services.agent_tools import AgentToolsService


def _parse_uuid(value: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This action requires an authenticated user. Please log in.",
        )


router = APIRouter()


@router.get(
    "/policies",
    response_model=list[AgentPolicyOut],
    summary="List user policies",
    description="Returns all policies for the user associated with the given session_id.",
)
async def agent_list_policies(
    session_id: str,
    _: AgentAuth,
    db: DBSession,
):
    return await AgentToolsService(db).list_policies(_parse_uuid(session_id))


@router.post(
    "/quotes",
    response_model=AgentQuoteOut,
    summary="Create a quote",
    description="Persists a quote with premium calculated by the agent from RAG pricing data.",
)
async def agent_create_quote(
    body: AgentQuoteCreate,
    _: AgentAuth,
    db: DBSession,
):
    return await AgentToolsService(db).create_quote(body)


@router.post(
    "/policies/{policy_id}/cancel",
    response_model=AgentPolicyOut,
    summary="Cancel a policy",
    description="Cancels an active policy. policy_id accepts either a UUID or a policy number (e.g. IP-XXXXXXXX).",
)
async def agent_cancel_policy(
    policy_id: str,
    session_id: str,
    _: AgentAuth,
    db: DBSession,
):
    return await AgentToolsService(db).cancel_policy(policy_id, _parse_uuid(session_id))


@router.post(
    "/quotes/{quote_id}/confirm",
    response_model=AgentPolicyOut,
    summary="Confirm payment for a quote",
    description="Simulates payment, creates an active policy, and returns it.",
)
async def agent_confirm_payment(
    quote_id: uuid.UUID,
    session_id: str,
    _: AgentAuth,
    db: DBSession,
):
    return await AgentToolsService(db).confirm_payment(quote_id, _parse_uuid(session_id))
