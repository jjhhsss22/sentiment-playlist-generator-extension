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

def latency_spike(metrics, baseline_ms=1500):
    """
    flag raised if maximum latency exceeds baseline ms
    """

    return metrics["latency_max"] >= baseline_ms * 2
