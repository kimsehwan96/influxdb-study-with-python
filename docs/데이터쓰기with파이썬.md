# 파이썬 클라이언트 라이브러리를 이용한 데이터 쓰기 작업

## Python client library

파이썬 스크립트와 응용프로그램을 InfluxDB와 통합하기 위해서 InfluxDB Python client library를 사용하세요.  

## 사전 준비 사항

1. InfluxDB 파이썬 라이브러리를 설치하기
    - `pip install influxdb-client` 혹은
    - `python3 -m pip install influxdb-client`

2. InfluxDB가 실행중인지 확인해보세요. 
    - `http://localhost:8086`를 접속해보세요.

## 파이썬을 통해 InfluxDB에 데이터 쓰기

- 파이썬 라이브러리와 함께 line protocol을 이용하여 데이터 쓰기작업을 해봅니다.

1. 파이썬 프로그램에서 InfluxDB 클라이언트 라이브러리을 import하세요.

```python3
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
```

2. 사용하고자 하는 버킷명, 조직명, 그리고 토큰값을 변수로 정의하세요

```python3
bucket = "<my-bucket>"
org = "<my-org>"
token = "<my-token>"
# Store the URL of your InfluxDB instance
url="http://localhost:8086"
```

3. 클라이언트를 객체화 하세요. InfluxDBClient 객체는 3개의 kwargs를 받습니다. url, org, token 이 세게입니다.

```python3
client = influxdb_client.InfluxDBClient(
  url=url,
  token=token,
  org=org
)
```

- 이 상태에서 client 객체는 write_api 메소드를 사용 가능합니다.

4. client 객체의 write_api 메소드를 이용해서  write client를 객체화하세요.

```python3
write_api = client.write_api(write_options=SYNCHRONOUS)
```

5. 포인트 객체를 하나 생성하고, API write 객체(write_api)를 이용해서 InfluxDB에 값을 넣어보세요.
    - wirte 메서드는 3개의 args(required)를 받습니다. bucket, org, 그리고 record 입니다.

```python3
p = influxdb_client.Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
write_api.write(bucket=bucket, org=org, record=p)
```

## 쓰기 스크립트를 완성해봅시다

```python3
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "<my-bucket>"
org = "<my-org>"
token = "<my-token>"
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
```

