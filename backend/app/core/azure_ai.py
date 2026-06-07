from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from app.core.config import settings


def make_openai_client():
    """Return an OpenAI-compatible client bound to the Foundry project."""
    project = AIProjectClient(
        endpoint=settings.azure_ai_project_base_endpoint,
        credential=DefaultAzureCredential(),
        allow_preview=True,
    )
    return project.get_openai_client()
