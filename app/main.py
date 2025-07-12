import os
import json
import time
import boto3
import psycopg2
import logging
import geojson

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("geojson-ingest")

# ENV vars
region = os.getenv("AWS_REGION", "us-east-1")
sqs_queue_url = os.getenv("SQS_QUEUE_URL")
secret_arn = os.getenv("SECRET_ARN")
table_name = os.getenv("TABLE_NAME", "geojson_data")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT")
host_endpoint = os.getenv("HOST_ENDPOINT")

sqs = boto3.client("sqs", region_name=region)
s3 = boto3.client("s3", region_name=region)
secrets = boto3.client("secretsmanager", region_name=region)


def fetch_db_credentials(secret_arn):
    response = secrets.get_secret_value(SecretId=secret_arn)
    return json.loads(response["SecretString"])


def connect_postgres(credentials):
    return psycopg2.connect(
        host=host_endpoint,
        dbname=db_name,
        user=credentials["username"],
        password=credentials["password"],
        port=db_port
    )


def process_s3_event(event):
    logger.info(f"Message body: {event['Body']}")
    msg = json.loads(event["Body"])
    if isinstance(msg, str):
        msg = json.loads(msg)
    if "Records" not in msg:
        logger.error("No 'Records' key in SQS message body")
        return
    record = msg["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]
    logger.info(f"Processing file: s3://{bucket}/{key}")
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')
    geojson_obj = geojson.loads(content)
    logger.info(f"geojson_obj type: {type(geojson_obj)}")
    logger.info(f"geojson_obj: {geojson_obj}")

    # Check for is_valid, but log the result
    logger.info(f"GeoJSON is_valid: {getattr(geojson_obj, 'is_valid', 'N/A')}")
    if hasattr(geojson_obj, 'is_valid') and not geojson_obj.is_valid:
        logger.error("Invalid GeoJSON")
        return

    # Try both dict and attribute access for features
    if isinstance(geojson_obj, dict) and geojson_obj.get("type") == "FeatureCollection":
        features = geojson_obj["features"]
    elif isinstance(geojson_obj, dict) and geojson_obj.get("type") == "Feature":
        features = [geojson_obj]
    else:
        logger.error(f"Unsupported or invalid GeoJSON type: {geojson_obj.get('type')}")
        return

    logger.info(f"Found {len(features)} features in GeoJSON.")

    creds = fetch_db_credentials(secret_arn)
    try:
        with connect_postgres(creds) as conn:
            with conn.cursor() as cur:
                for feature in features:
                    geom = json.dumps(feature["geometry"])
                    props = json.dumps(feature.get("properties", {}))
                    try:
                        cur.execute(
                            f"INSERT INTO {table_name} (geom, props) VALUES (ST_GeomFromGeoJSON(%s), %s);",
                            (geom, props)
                        )
                        logger.info(f"Inserted feature: {props}")
                    except Exception as e:
                        logger.error(f"Insert failed: {e}")
            conn.commit()
        logger.info("Successfully inserted all features into the database.")
    except Exception as e:
        logger.error(f"Database insertion failed: {e}")
    logger.info("File processed and loaded successfully.")


def poll_sqs():
    logger.info("Polling SQS for S3 events...")
    while True:
        resp = sqs.receive_message(
            QueueUrl=sqs_queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )
        messages = resp.get("Messages", [])
        for msg in messages:
            try:
                process_s3_event(msg)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
            sqs.delete_message(
                QueueUrl=sqs_queue_url,
                ReceiptHandle=msg["ReceiptHandle"]
            )
        time.sleep(5)


if __name__ == "__main__":
    poll_sqs()
