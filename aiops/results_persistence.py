from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from db_connection import get_db
from dbmodel import AnomalyResult
from fingerprint import anomaly_fingerprint


def persist_anomalies(anomalies, window_start, window_end, lookback_hours=1):
    """
    persist anomaly decisions idempotently with noise reduction.

    noise reduction: If a similar anomaly was detected within the last N hours,
    update the existing record instead of creating a duplicate.

    args:
        anomalies: list of anomaly dicts
        window_start: datetime object
        window_end: datetime object
        lookback_hours: How far back to check for similar anomalies
    """
    for db in get_db():
        try:
            cutoff_time = datetime.now() - timedelta(hours=lookback_hours)

            for anomaly in anomalies:
                fp = anomaly_fingerprint({
                    "type": anomaly["type"],
                    "task": anomaly.get("task"),
                    "error_type": anomaly.get("error_type"),
                    "window_start": window_start.isoformat(),
                })

                # check if similar anomaly exists recently
                existing = db.query(AnomalyResult).filter(
                    and_(
                        AnomalyResult.type == anomaly["type"],
                        AnomalyResult.task == anomaly.get("task"),
                        AnomalyResult.error_type == anomaly.get("error_type"),
                        AnomalyResult.detected_at > cutoff_time
                    )
                ).first()

                if existing:  # instead of silently ignoring duplicates, we increase count.
                    # update existing anomaly (noise reduction)
                    existing.count = (existing.count or 0) + anomaly.get("count", 1)
                    existing.window_end = window_end
                    existing.last_seen = datetime.now()
                    existing.metrics = anomaly.get("metrics")  # update with latest metrics

                    # escalate severity if needed
                    if anomaly["severity"] == "critical" and existing.severity != "critical":
                        existing.severity = "critical"

                else:
                    # create new anomaly record
                    row = AnomalyResult(
                        type=anomaly["type"],
                        severity=anomaly["severity"],
                        task=anomaly.get("task"),
                        service=anomaly.get("service"),
                        error_type=anomaly.get("error_type"),
                        count=anomaly.get("count", 1),
                        metrics=anomaly.get("metrics"),
                        dlq_key=anomaly.get("dlq_key"),
                        window_start=window_start,
                        window_end=window_end,
                        fingerprint=fp,
                    )
                    db.add(row)

            db.commit()

        except IntegrityError:
            db.rollback()