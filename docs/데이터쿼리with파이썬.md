## 파이썬을 이용해 데이터 쿼리하기

1. Query client를 객체화 하세요

```python3
query_api = client.query_api()
```

2. Flux 문법의 쿼리를 작성하세요

```python3
query = ‘ from(bucket:"my-bucket")\
|> range(start: -10m)\
|> filter(fn:(r) => r._measurement == "my_measurement")\
|> filter(fn: (r) => r.location == "Prague")\
|> filter(fn:(r) => r._field == "temperature" )‘
```

- 쿼리 클라이언트는 Flux쿼리를 influxdb에 보내고,table 구조의 Flux오브젝트를 리턴받습니다.

3. 두개의 파라미터 org와 query를 query() 메서드에 전달합니다

```python3
result = client.query_api().query(org=org, query=query)
```

4. Flux 객체안의 테이블과 레코드를 순회합니다(Iterate)
    - get_value() 메서드는 값을 반환합니다.
    - get_field() 메서드는 필드를 반환합니다.

```python3
results = []
for table in result:
for record in table.records:
results.append((record.get_field(), record.get_value()))

print(results)
[(temperature, 25.3)]
```

### Flux 객체는 데이터에 접근하기 위해 다음과 같은 메서드들을 제공합니다.

- `get_measurement()` : 레코드의 measurement 이름을 반환합니다.
- `get_field()` : 필드 이름을 반환합니다.
- `get_value()` : 필드의 실제 값을 반환합니다.
- `values()` : 칼럼의 값들의 map 객체를 반환합니다.
- `values.get("your-tag")` : 주어진 칼럼의 레코드에서 값을 반환합니다.
- `get_time()` : 레코드의 시간값을 반환합니다
- `get_start()`
- `get_stop()`

### 예제 쿼리 스크립트 완성

```python3

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "<your token>"
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
# 출력값 : [(temperature, 25.3)]
```

- 공식 사이트 파이썬 예제는 실제로 동작하지 않음. 오류 부분을 수정하여 작성하였음.

https://docs.influxdata.com/influxdb/v2.0/tools/client-libraries/python/

