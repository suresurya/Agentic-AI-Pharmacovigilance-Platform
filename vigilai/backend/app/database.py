# Mock database for development (bypasses Motor/pymongo version issues)
# In-memory storage for demo purposes

_narratives = {}
_reports = {}
_entities = {}
_actions = {}
_whoart_terms = {}


async def init_db():
    """Initialize mock database - no external dependencies"""
    print("✓ Mock database initialized (in-memory storage)")
    return True
