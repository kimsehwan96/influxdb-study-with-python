from datetime import datetime
from influxdb_client import Point, WritePrecision
from time import sleep
from random import uniform

class RandomConfig:
    def __init__(self, measurement_name:str, tag_pair: list or tuple, field_name: str):
        self.measurement_name = measurement_name
        self.tag_pair = tag_pair
        self.field_name = field_name
        self.start = 0
        self.end = 100
    
    def set_random_range(self, start, end):
        self.start = start
        self.end = end

class RandomGenrator:
    def __init__(self, random_config:RandomConfig):
        self.measurement_name = random_config.measurement_name
        self.tag_pair = random_config.tag_pair
        self.field_name = random_config.field_name
        self.start = random_config.start
        self.end = random_config.end
    
    def get_random_point(self) -> Point:
        self.point = Point(self.measurement_name)\
            .tag(self.tag_pair[0], self.tag_pair[1])\
            .field(self.field_name, uniform(self.start, self.end))\
            .time(datetime.utcnow(), WritePrecision.NS)
        
        #이렇게 메서드 체이닝이 가능 한 이유가. 저 메서드들이 모두 return self 라서 그럼
        #build 패턴에서 많이 보던 패턴이지?
        
        return self.point


if __name__ == "__main__":
    config = RandomConfig("mem", ["user", "user1"], "usage_percent")
    config.set_random_range(1, 100)

    rg = RandomGenrator(config)

    while True:
        sleep(1)
        print(rg.get_random_point())

#흠. Point 인스턴스에 대해서 __str__ 이 정의가 안되어있는건 좀 문제네..