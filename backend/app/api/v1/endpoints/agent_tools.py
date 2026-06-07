import uuid
from fastapi import APIRouter
from app.core.deps import AgentAuth, DBSession
from app.schemas.agent import AgentQuoteCreate, AgentQuoteOut, AgentPolicyOut
from app.services.agent_tools import AgentToolsService

router = APIRouter()


@router.get(
    "/policies",
    response_model=list[AgentPolicyOut],
    summary="List user policies",
    description="Returns all policies for the user associated with the given thread_id.",
)
async def agent_list_policies(
    thread_id: uuid.UUID,
    _: AgentAuth,
    db: DBSession,
):
    return await AgentToolsService(db).list_policies(thread_id)


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
    description="Cancels an active policy belonging to the user associated with thread_id.",
)
async def agent_cancel_policy(
    policy_id: uuid.UUID,
    thread_id: uuid.UUID,
    _: AgentAuth,
    db: DBSession,
):
    return await AgentToolsService(db).cancel_policy(policy_id, thread_id)
