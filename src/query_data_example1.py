
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "s7osywpu7TghUKAMs9k1HYZkHsKgUG6YkvxFdGjGSsgMLEVl0TvxqvLByAeyQiY_1tT1UdjfPf1TxZbHFs6gUg=="
#이 토큰은 sehwan이라는 조직에 대해서 유효한 토큰임.
org = "sehwan"
bucket = "testBucket"

client = InfluxDBClient(url="http://localhost:8086", token=token)

query_api = client.query_api()
query = 'from(bucket:"{}")\
|> range(start: -10m)\
|> filter(fn:(r) => r._measurement == "my_measurement")\
|> filter(fn: (r) => r.location == "Prague")\
|> filter(fn:(r) => r._field == "temperature" )'.format(bucket)
result = client.query_api().query(org=org, query=query)
results = []
for table in result:
    for record in table.records:
        results.append((record.get_field(), record.get_value()))

print(results)