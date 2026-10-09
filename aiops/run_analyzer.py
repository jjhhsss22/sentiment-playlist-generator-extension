import time
from datetime import datetime
from db_connection import SessionLocal, Base, engine
from anomaly_analyzer import analyze
from results_persistence import persist_anomalies

Base.metadata.create_all(bind=engine)  # Ensure anomaly_results table exists


def run(interval_seconds=300):
    """
    Periodically run anomaly analysis and persist results.
    """

    while True:
        current_time = time.time()
        window_end_ts = (current_time // 60) * 60  # Round down to minute boundary
        window_start_ts = window_end_ts - interval_seconds

        # Convert to datetime objects
        window_start_dt = datetime.fromtimestamp(window_start_ts)
        window_end_dt = datetime.fromtimestamp(window_end_ts)

        # Expected: list[dict] of anomaly payloads
        anomalies = analyze()

        if anomalies:
            persist_anomalies(anomalies, window_start_dt, window_end_dt)

        time.sleep(interval_seconds)


if __name__ == "__main__":
    run()