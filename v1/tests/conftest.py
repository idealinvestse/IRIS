"""
IRIS v6.0 - Test Configuration
Pytest fixtures och test-setup
"""

import pytest
import asyncio
from typing import Generator
import os

# Sätt test-miljövariabler
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["GDPR_ENABLED"] = "true"
os.environ["XAI_API_KEY"] = "test-key-12345"

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create test database"""
    from src.core.database import Database
    
    db = Database(database_url="sqlite+aiosqlite:///:memory:")
    await db.init_database()
    
    yield db
    
    await db.close()

@pytest.fixture
def test_settings():
    """Get test settings"""
    from src.core.config import get_settings
    return get_settings()

@pytest.fixture
def sample_query():
    """Sample query for testing"""
    return "Vad är OMX-kursen idag?"

@pytest.fixture
def sample_queries():
    """Multiple sample queries"""
    return [
        "Hur är vädret i Stockholm?",
        "Analysera svenska ekonomin",
        "Senaste nyheterna från Sverige",
        "SCB befolkningsstatistik"
    ]
