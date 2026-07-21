import boto3
import requests
import os
import logging
from datetime import datetime,timezone

"""
 - Logging Config
 - The format is logging module specific.
 - '__name__' will be either '__main__' or filename if imported.
"""
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

REGION        = os.getenv("AWS_REGION", "ap-southeast-1")
HEALTH_URL    = os.getenv("HEALTH_URL", "http://localhost:5000/health")
NAMESPACE     = "FlaskMicroservice"
INSTANCE_ID   = os.getenv("INSTANCE_ID", "local")

def get_health_status():
	try:
		response = requests.get(HEALTH_URL, timeout=5)
		data = response.json()
		status = data.get("status", "unknown")
		db_ok  = 1 if data.get("db") == "ok" else 0
		app_ok = 1 if status == "ok" else 0
		return app_ok, db_ok, response.elapsed.total_seconds() * 1000
	except Exception as e:
		logger.error(f"Health check failed: {e}")
		return 0, 0, 0
	
def push_metrics(app_ok, db_ok, response_time_ms):
	"""
	 - Create Custom Metrics for CloudWatch under Namespace "FlaskMicroservice"
	 - Cron job will run this python script at intervals
	 - and keep feeding data to CloudWatch via custom metrics.
	"""
	client = boto3.client("cloudwatch", region_name=REGION)
	
	metric_data = [
	{
		"MetricName": "AppHealthStatus",
		"Dimensions": [{"Name": "InstanceId", "Value": INSTANCE_ID}],
		"Value":      float(app_ok),
		"Unit":       "Count",
		"Timestamp":  datetime.now(timezone.utc),
	},
	{
		"MetricName": "DBHealthStatus",
		"Dimensions": [{"Name": "InstanceId", "Value": INSTANCE_ID}],
		"Value":      float(db_ok),
		"Unit":       "Count",
		"Timestamp":  datetime.now(timezone.utc),
	},
	{
		"MetricName": "HealthCheckResponseTime",
		"Dimensions": [{"Name": "InstanceId", "Value": INSTANCE_ID}],
		"Value":      float(response_time_ms),
		"Unit":       "Milliseconds",
		"Timestamp":  datetime.now(timezone.utc),
	},
]

	client.put_metric_data(
		Namespace=NAMESPACE,
		MetricData=metric_data,
	)

	logger.info(
		f"Pushed metrics — App: {app_ok}, DB: {db_ok}, "
		f"ResponseTime: {response_time_ms:.1f}ms"
	)


if __name__ == "__main__":
	app_ok, db_ok, response_time = get_health_status()
	push_metrics(app_ok, db_ok, response_time)