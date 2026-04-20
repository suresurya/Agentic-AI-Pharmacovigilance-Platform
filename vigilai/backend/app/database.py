from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings


_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_url)
    return _client


async def init_db():
    from app.models.narrative import Narrative
    from app.models.entity import Entity
    from app.models.adr_report import ADRReport
    from app.models.officer_action import OfficerAction
    from app.models.whoart_term import WHOARTTerm

    client = get_client()
    await init_beanie(
        database=client[settings.mongodb_db],
        document_models=[Narrative, Entity, ADRReport, OfficerAction, WHOARTTerm],
    )
