from contextlib import asynccontextmanager
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from app.core.config import settings


@asynccontextmanager
async def get_ai_client():
    async with AIProjectClient.from_connection_string(
        conn_str=settings.azure_ai_project_connection_string,
        credential=DefaultAzureCredential(),
    ) as client:
        yield client
