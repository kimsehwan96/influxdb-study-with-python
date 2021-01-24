from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from . import TOKEN

# You can generate a Token from the "Tokens Tab" in the UI
token = TOKEN
#이 토큰은 sehwan이라는 조직에 대해서 유효한 토큰임.
org = "sehwan"
bucket = "testBucket"

client = InfluxDBClient(url="http://localhost:8086", token=token)

write_api = client.write_api(write_options=SYNCHRONOUS)

data = "mem,host=host1 used_percent=23.43234543"
write_api.write(bucket, org, data)

point = Point("mem")\
  .tag("host", "host1")\
  .field("used_percent", 23.43234543)\
  .time(datetime.utcnow(), WritePrecision.NS)

write_api.write(bucket, org, point)

query = f'from(bucket: \\"{bucket}\\") |> range(start: -1h)'
tables = client.query_api().query(query, org=org)