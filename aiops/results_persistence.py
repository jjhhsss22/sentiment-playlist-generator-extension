from datetime import datetime
from sqlalchemy.exc import IntegrityError

from db_connection import get_db
from dbmodel import AnomalyResult
from fingerprint import anomaly_fingerprint


def persist_anomalies(anomalies, window_start, window_end):
    """
    Persist anomaly decisions idempotently.

    Args:
        anomalies: list of anomaly dicts
        window_start: datetime object
        window_end: datetime object
    """
    for db in get_db():
        try:
            for anomaly in anomalies:
                fp = anomaly_fingerprint({
                    "type": anomaly["type"],
                    "task": anomaly.get("task"),
                    "error_type": anomaly.get("error_type"),
                    "window_start": window_start.isoformat(),
                })

                row = AnomalyResult(
                    type=anomaly["type"],
                    severity=anomaly["severity"],
                    task=anomaly.get("task"),
                    service=anomaly.get("service"),
                    error_type=anomaly.get("error_type"),
                    count=anomaly.get("count"),
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