from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi
from random import uniform
from threading import Thread, Timer
from time import sleep


TOKEN = "rjYdDj3e0zHkjRTIV_2b7O_Sqk_e-KV2re24FTDM8uHwvMDkdnzwTwfz6igWoBrTyjw2K2ll3dvG73L8Cjx6Ig=="
ORG = "sehwan"
BUCKET = "testBucket"

client = InfluxDBClient(url="http://localhost:8086", token=TOKEN)
write_api = client.write_api(write_options=SYNCHRONOUS)
#데이터 쓸 api 인스턴스를 생성함.

args=(write_api,"mem",["host", "host1"], "user_percent")
#데이터의 timestamp를 DB에서 찍게되는 예제임.
def write_thread(apiclient: WriteApi, measurement: str, tag_pair:tuple or list, field_key: str) -> None:
    line_data = "{},{}={} {}={}".format(measurement, tag_pair[0], tag_pair[1], field_key, uniform(1,100))
    apiclient.write(BUCKET, ORG, line_data)
    print("data was sent : {}".format(line_data))

    Timer(1.0, write_thread,args=args).start()

write_thread(*args)

    