from dlq_reader import read_recent_dlq_entries
from metrics_reader import list_tasks, read_task_metrics
from anomaly_rules import *

def analyze():
    anomalies = []

    dlq_entries = read_recent_dlq_entries(300)
    if dlq_entries:
        anomalies.append({
            "type": "DLQ_ACTIVITY",
            "severity": "critical",
            "count": len(dlq_entries),
            "examples": dlq_entries[:3],
        })

    for task in list_tasks():
        metric = read_task_metrics(task)

        if high_error_rate(metric):
            anomalies.append({
                "type": "HIGH_ERROR_RATE",
                "task": task,
                "metrics": metric,
                "severity": "high",
            })

        if excessive_retries(metric):
            anomalies.append({
                "type": "HIGH_RETRY_RATE",
                "task": task,
                "metrics": metric,
                "severity": "medium",
            })

        if latency_spike(metric):
            anomalies.append({
                "type": "LATENCY_SPIKE",
                "task": task,
                "metrics": metric,
                "severity": "medium",
            })

    return anomalies
