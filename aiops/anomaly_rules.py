"""
rules for aiops
these rules will be used to flag any anomalies in the current window
"""

def high_error_rate(metrics, threshold=0.15):
    """
    flag raised if 15% of all requests exceeds error threshold
    """
    total = metrics["success"] + metrics["errors"]
    return total > 0 and (metrics["errors"] / total) >= threshold

def excessive_retries(metrics, max_retries=5):
    """
    flag raised if a certain task retries exceeds max retries
    """
    return metrics["retries"] >= max_retries

def excessive_dlq_recurrence(dlq_entry, threshold=5):
    """
    flag if the same failure repeats many times.
    """
    return dlq_entry["count"] >= threshold

def latency_spike(metrics, baseline_ms=1500):
    """
    flag raised if maximum latency exceeds baseline ms
    """
    return metrics["latency_max"] >= baseline_ms * 2

def latency_p95_spike(metrics, baseline_p95_ms=1000):
    """
    flag raised if p95 latency exceeds baseline.
    more reliable than max latency (ignores outliers).
    """
    return metrics["latency_p95"] >= baseline_p95_ms * 2

def latency_p99_degradation(metrics, baseline_p99_ms=2000):
    """
    flag raised if p99 latency shows degradation.
    catches tail latency issues.
    """
    return metrics["latency_p99"] >= baseline_p99_ms * 1.5