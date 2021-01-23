import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

token = "s7osywpu7TghUKAMs9k1HYZkHsKgUG6YkvxFdGjGSsgMLEVl0TvxqvLByAeyQiY_1tT1UdjfPf1TxZbHFs6gUg=="
org = "sehwan"
bucket = "testBucket"
# Store the URL of your InfluxDB instance
url="http://localhost:8086"

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)

p = influxdb_client.Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
write_api.write(bucket=bucket, org=org, record=p)