import hashlib
import json


def anomaly_fingerprint(data: dict) -> str:
    """stable fingerprint for anomaly deduplication and table flooding."""

    dumped = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(dumped.encode()).hexdigest()