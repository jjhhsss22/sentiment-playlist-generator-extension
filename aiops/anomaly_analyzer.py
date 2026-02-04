from dlq_reader import read_recent_dlq_entries
from metrics_reader import list_tasks, read_task_metrics
from anomaly_rules import *


def analyze():
    anomalies = []

    dlq_entries = read_recent_dlq_entries(300)  # DLQ analysis (fingerprinted)

    for entry in dlq_entries:
        if excessive_dlq_recurrence(entry):
            anomalies.append({
                "type": "REPEATED_DLQ_FAILURE",
                "severity": "critical",
                "task": entry["task"],
                "service": entry["service"],
                "error_type": entry["error_type"],
                "count": entry["count"],
                "dlq_key": entry["dlq_key"],
                "first_seen": entry["first_seen"],
                "last_seen": entry["last_seen"],
            })


    for task in list_tasks():  # metrics analysis
        metric = read_task_metrics(task)

        # extract service from task name
        service = task.split(".")[0] if "." in task else "unknown"

        if high_error_rate(metric):
            anomalies.append({
                "type": "HIGH_ERROR_RATE",
                "severity": "high",
                "task": task,
                "service": service,
                "metrics": metric,
            })

        if excessive_retries(metric):
            anomalies.append({
                "type": "HIGH_RETRY_RATE",
                "severity": "medium",
                "task": task,
                "service": service,
                "metrics": metric,
            })

        if latency_spike(metric):
            anomalies.append({
                "type": "LATENCY_SPIKE",
                "severity": "medium",
                "task": task,
                "service": service,
                "metrics": metric,
            })

        if latency_p95_spike(metric):
            anomalies.append({
                "type": "LATENCY_P95_SPIKE",
                "severity": "high",
                "task": task,
                "service": service,
                "metrics": metric,
            })

        if latency_p99_degradation(metric):
            anomalies.append({
                "type": "LATENCY_P99_DEGRADATION",
                "severity": "medium",
                "task": task,
                "service": service,
                "metrics": metric,
            })

    return anomalies