from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi
from random_genrator import RandomConfig, RandomGenrator
from threading import Thread
from time import sleep


TOKEN = "sZr7ksaAkHQVBLIF7OGckgtoYaI358hSYupqeLUfxJRVAMCaJjidX-omUUWUeOV9YIm4kxUk8IYarkDFEb-cIw=="
ORG = "sehwan"
BUCKET = "testBucket"

client = InfluxDBClient(url="http://localhost:8086", token=TOKEN)
write_api = client.write_api(write_options=SYNCHRONOUS)
#데이터 쓸 api 인스턴스를 생성함.

config_1 = RandomConfig("mem", ["user", "user1"], "usage_percent")
config_1.set_random_range(1, 100)

config_2 = RandomConfig("mem", ["user", "user2"], "usage_percent")
config_2.set_random_range(1, 100)

rg1 = RandomGenrator(config_1)
rg2 = RandomGenrator(config_2)

rgs = [rg1, rg2]

def write_thread(rg:RandomGenrator, write_api: WriteApi, bucket, org):
    while True:
        write_api.write(bucket, org, rg.get_random_point())
        print("data was sent!")
        sleep(1)

th1 = Thread(target=write_thread, args=(rg1, write_api, BUCKET, ORG))
th2 = Thread(target=write_thread, args=(rg2, write_api, BUCKET, ORG))

th1.start()
th2.start()

    