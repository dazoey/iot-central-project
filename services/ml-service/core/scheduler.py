import logging
from apscheduler.schedulers.background import BackgroundScheduler
from core.db import fetch_sensor_telemetry_history
from models.anomaly import IsolationForestAnomalyDetector

# Logger Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoRetrainingPipeline")

class AutoRetrainingPipeline:
    """
    Auto-Retraining ML Pipeline.
    Periodically fetches historical sensor telemetry from TimescaleDB and retrains
    Isolation Forest anomaly detection models automatically.
    """
    def __init__(self, iso_detector: IsolationForestAnomalyDetector):
        self.iso_detector = iso_detector
        self.scheduler = BackgroundScheduler()

    def retrain_all_models(self):
        """
        Executes automatic retraining cycle for active sensors in TimescaleDB.
        """
        logger.info("[AUTO-RETRAIN] Triggered automatic ML model retraining cycle...")
        try:
            # Query sample sensor IDs from DB
            sensor_ids = [1, 2, 3, 4]
            total_retrained = 0

            for sensor_id in sensor_ids:
                db_records = fetch_sensor_telemetry_history(sensor_id, limit=300)
                if db_records and len(db_records) >= 10:
                    values = [r["value"] for r in db_records]
                    self.iso_detector.train(values)
                    total_retrained += 1
                    logger.info(f"[AUTO-RETRAIN SUCCESS] Sensor ID {sensor_id} retrained with {len(values)} data points.")
            
            logger.info(f"[AUTO-RETRAIN COMPLETE] Successfully retrained {total_retrained} sensor models.")
        except Exception as e:
            logger.error(f"[AUTO-RETRAIN ERROR] Retraining cycle failed: {str(e)}")

    def start_scheduler(self, interval_hours: int = 24):
        """
        Starts the background scheduler job.
        """
        if not self.scheduler.running:
            # Schedule periodic retraining job
            self.scheduler.add_job(
                self.retrain_all_models,
                'interval',
                hours=interval_hours,
                id='auto_retrain_ml_job',
                replace_existing=True
            )
            self.scheduler.start()
            logger.info(f"[AUTO-RETRAIN SCHEDULER] Started background scheduler job (Runs every {interval_hours} hours).")

    def stop_scheduler(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("[AUTO-RETRAIN SCHEDULER] Background scheduler stopped.")
