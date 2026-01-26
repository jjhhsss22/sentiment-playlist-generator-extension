import hashlib
import json


def anomaly_fingerprint(data: dict) -> str:
    """
    Stable fingerprint for anomaly deduplication.
    """
    dumped = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(dumped.encode()).hexdigest()