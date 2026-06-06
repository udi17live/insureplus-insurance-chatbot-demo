from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from app.core.config import settings


def _make_project_client() -> AIProjectClient:
    return AIProjectClient(
        endpoint=settings.azure_ai_project_base_endpoint,
        credential=DefaultAzureCredential(),
        allow_preview=True,
    )


async def create_thread() -> str:
    async with _make_project_client() as project_client:
        openai_client = project_client.get_openai_client(agent_name=settings.primary_agent_id)
        thread = await openai_client.beta.threads.create()
        return thread.id


def make_project_client() -> AIProjectClient:
    return _make_project_client()
