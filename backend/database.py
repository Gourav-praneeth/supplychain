from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

Base = declarative_base()


class Lot(Base):
    """
    Represents a food lot (NFT) tracked on the blockchain.
    Mirrors on-chain data for fast querying.
    """
    __tablename__ = "lots"

    token_id = Column(Integer, primary_key=True, index=True)
    owner_address = Column(String(42), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    is_recalled = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    history_entries = relationship("HistoryEntry", back_populates="lot")


class HistoryEntry(Base):
    """
    Represents an audit trail entry for a lot.
    Indexed from blockchain events.
    """
    __tablename__ = "history_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_id = Column(Integer, ForeignKey("lots.token_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)
    stakeholder_address = Column(String(42), nullable=False)
    ipfs_hash = Column(String(100), nullable=False)
    event_type = Column(String(50), nullable=False)
    transaction_hash = Column(String(66), nullable=False, unique=True)
    block_number = Column(Integer, nullable=False)

    lot = relationship("Lot", back_populates="history_entries")


class RecallEvent(Base):
    """
    Stores recall events triggered by regulators.
    """
    __tablename__ = "recall_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_id = Column(Integer, ForeignKey("lots.token_id"), nullable=False, index=True)
    regulator_address = Column(String(42), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    transaction_hash = Column(String(66), nullable=False, unique=True)
    block_number = Column(Integer, nullable=False)


engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize database tables.
    PSEUDOCODE:
    1. Create all tables defined in Base metadata
    2. Run any necessary migrations
    3. Set up indexes for query optimization
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency injection for FastAPI routes.
    PSEUDOCODE:
    1. Create a new database session
    2. Yield the session to the route handler
    3. Close session after request completes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
