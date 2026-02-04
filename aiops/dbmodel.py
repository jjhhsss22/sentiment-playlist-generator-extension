from sqlalchemy import (
    Column,
    Integer,
    String,
    JSON,
    DateTime,
    Index,
)
from sqlalchemy.sql import func
from db_connection import Base

class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id = Column(Integer, primary_key=True)

    # what happened
    type = Column(String(64), nullable=False)
    severity = Column(String(16), nullable=False)

    # scope
    task = Column(String(128), nullable=True)
    service = Column(String(64), nullable=True)

    # timing
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    detected_at = Column(DateTime, server_default=func.now())  # for lookback queries that prevent duplicate anomaly reports
    last_seen = Column(DateTime, nullable=True)

    # evidence
    metrics = Column(JSON, nullable=True)
    dlq_key = Column(String(255), nullable=True)
    error_type = Column(String(64), nullable=True)
    count = Column(Integer, nullable=True)

    # deduplication
    fingerprint = Column(String(64), nullable=False)

    __table_args__ = (
        Index("idx_anomaly_fingerprint", "fingerprint", unique=True),
        Index("idx_anomaly_lookup", "type", "task", "detected_at"),  # for noise reduction queries
    )
