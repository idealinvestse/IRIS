"""
IRIS v6.0 - Database Abstraction Layer
Hanterar både SQLite (utveckling) och PostgreSQL (produktion)
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Text, select
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

class QueryLog(Base):
    """Logg för användarfrågor (GDPR-kompatibel)"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True)
    query_hash = Column(String(64), index=True)  # SHA-256 hash, inte klartext
    profile_used = Column(String(50))
    sources_used = Column(JSON)
    processing_time = Column(Integer)  # millisekunder
    success = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    gdpr_consent = Column(Boolean, default=False)
    
class ConsentRecord(Base):
    """GDPR-samtycken"""
    __tablename__ = "consent_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True)
    analytics_consent = Column(Boolean, default=False)
    data_processing_consent = Column(Boolean, default=False)
    consent_given_at = Column(DateTime, default=datetime.utcnow)
    consent_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    
class CacheEntry(Base):
    """Cache-tabell för fallback utan Redis"""
    __tablename__ = "cache_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, index=True)
    cache_value = Column(Text)
    expires_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    """
    Databas-abstraktion för IRIS v6.0
    Stödjer både SQLite och PostgreSQL
    """
    
    def __init__(self, database_url: Optional[str] = None):
        from src.core.config import get_settings
        settings = get_settings()
        
        self.database_url = database_url or settings.database_url
        self.engine = None
        self.session_maker = None
        
        logger.info(f"📊 Databas konfigurerad: {self._mask_url(self.database_url)}")
    
    def _mask_url(self, url: str) -> str:
        """Maskera känslig information i databas-URL"""
        if "@" in url:
            parts = url.split("@")
            return f"{parts[0].split(':')[0]}://***@{parts[1]}"
        return url
    
    async def init_database(self):
        """Initialisera databasanslutning och skapa tabeller"""
        try:
            # Hantera SQLite vs PostgreSQL
            if self.database_url.startswith("sqlite"):
                # SQLite kräver aiosqlite
                db_url = self.database_url.replace("sqlite://", "sqlite+aiosqlite://")
            elif self.database_url.startswith("postgresql"):
                # PostgreSQL kräver asyncpg
                db_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
            else:
                db_url = self.database_url
            
            # Skapa async engine
            self.engine = create_async_engine(
                db_url,
                echo=False,  # Sätt till True för SQL-debugging
                pool_pre_ping=True,  # Kontrollera anslutningar innan användning
                pool_size=5,
                max_overflow=10
            )
            
            # Skapa session maker
            self.session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Skapa tabeller
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("✅ Databas initialiserad och tabeller skapade")
            
        except Exception as e:
            logger.error(f"❌ Fel vid databas-initialisering: {e}")
            raise
    
    async def close(self):
        """Stäng databasanslutning"""
        if self.engine:
            await self.engine.dispose()
            logger.info("🔒 Databasanslutning stängd")
    
    @asynccontextmanager
    async def get_session(self):
        """Ge en databassession med automatisk hantering"""
        if not self.session_maker:
            await self.init_database()
        
        async with self.session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Databasfel: {e}")
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """Kontrollera databashälsa"""
        try:
            async with self.get_session() as session:
                await session.execute(select(1))
            return True
        except Exception as e:
            logger.error(f"Databas hälsokontroll misslyckades: {e}")
            return False
    
    async def log_query(
        self,
        user_id: str,
        query_hash: str,
        profile: str,
        sources: list,
        processing_time: int,
        success: bool,
        gdpr_consent: bool
    ):
        """Logga en användarfråga (GDPR-kompatibel)"""
        try:
            async with self.get_session() as session:
                log_entry = QueryLog(
                    user_id=user_id,
                    query_hash=query_hash,
                    profile_used=profile,
                    sources_used=sources,
                    processing_time=processing_time,
                    success=success,
                    gdpr_consent=gdpr_consent
                )
                session.add(log_entry)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Kunde inte logga fråga: {e}")
    
    async def get_consent(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Hämta användarens GDPR-samtycke"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(ConsentRecord).where(ConsentRecord.user_id == user_id)
                )
                consent = result.scalar_one_or_none()
                
                if consent:
                    return {
                        "analytics": consent.analytics_consent,
                        "data_processing": consent.data_processing_consent,
                        "given_at": consent.consent_given_at.isoformat()
                    }
                return None
                
        except Exception as e:
            logger.error(f"Kunde inte hämta samtycke: {e}")
            return None
    
    async def update_consent(
        self,
        user_id: str,
        analytics: bool = False,
        data_processing: bool = False,
        ip_address: Optional[str] = None
    ):
        """Uppdatera GDPR-samtycke"""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    select(ConsentRecord).where(ConsentRecord.user_id == user_id)
                )
                consent = result.scalar_one_or_none()
                
                if consent:
                    # Uppdatera befintligt
                    consent.analytics_consent = analytics
                    consent.data_processing_consent = data_processing
                    consent.consent_updated_at = datetime.utcnow()
                    if ip_address:
                        consent.ip_address = ip_address
                else:
                    # Skapa nytt
                    consent = ConsentRecord(
                        user_id=user_id,
                        analytics_consent=analytics,
                        data_processing_consent=data_processing,
                        ip_address=ip_address
                    )
                    session.add(consent)
                
                await session.commit()
                logger.info(f"✅ Samtycke uppdaterat för användare: {user_id}")
                
        except Exception as e:
            logger.error(f"Kunde inte uppdatera samtycke: {e}")
            raise
    
    async def delete_user_data(self, user_id: str):
        """Radera all användardata (GDPR Rätten att bli glömd)"""
        try:
            async with self.get_session() as session:
                # Ta bort query logs
                await session.execute(
                    QueryLog.__table__.delete().where(QueryLog.user_id == user_id)
                )
                
                # Ta bort consent
                await session.execute(
                    ConsentRecord.__table__.delete().where(ConsentRecord.user_id == user_id)
                )
                
                await session.commit()
                logger.info(f"🗑️ Användardata raderad för: {user_id}")
                
        except Exception as e:
            logger.error(f"Kunde inte radera användardata: {e}")
            raise
    
    async def cleanup_old_data(self, days: int = 30):
        """Rensa gammal data enligt GDPR-retention policy"""
        try:
            cutoff_date = datetime.utcnow().replace(day=datetime.utcnow().day - days)
            
            async with self.get_session() as session:
                # Rensa gamla query logs
                await session.execute(
                    QueryLog.__table__.delete().where(QueryLog.created_at < cutoff_date)
                )
                
                # Rensa gamla cache entries
                await session.execute(
                    CacheEntry.__table__.delete().where(CacheEntry.expires_at < datetime.utcnow())
                )
                
                await session.commit()
                logger.info(f"🧹 Gammal data äldre än {days} dagar rensad")
                
        except Exception as e:
            logger.error(f"Kunde inte rensa gammal data: {e}")
