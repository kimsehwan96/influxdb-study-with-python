# coding: utf-8

from __future__ import absolute_import

import time
import unittest

import httpretty
import rx
from rx import operators as ops

import influxdb_client
from influxdb_client import WritePrecision, InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.client.write_api import WriteOptions, WriteApi, PointSettings


class BatchingWriteTest(unittest.TestCase):

    def setUp(self) -> None:
        httpretty.enable()
        httpretty.reset()

        conf = influxdb_client.configuration.Configuration()
        conf.host = "http://localhost"
        conf.debug = False

        self.influxdb_client = InfluxDBClient(url=conf.host, token="my-token")

        self.write_options = WriteOptions(batch_size=2, flush_interval=5_000, retry_interval=3_000)
        self._write_client = WriteApi(influxdb_client=self.influxdb_client, write_options=self.write_options)

    def tearDown(self) -> None:
        self._write_client.__del__()
        httpretty.disable()

    def test_batch_size(self):
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        self._write_client.write("my-bucket", "my-org",
                                 ["h2o_feet,location=coyote_creek level\\ water_level=1 1",
                                  "h2o_feet,location=coyote_creek level\\ water_level=2 2",
                                  "h2o_feet,location=coyote_creek level\\ water_level=3 3",
                                  "h2o_feet,location=coyote_creek level\\ water_level=4 4"])

        time.sleep(1)

        _requests = httpretty.httpretty.latest_requests

        self.assertEqual(2, len(_requests))
        _request1 = "h2o_feet,location=coyote_creek level\\ water_level=1 1\n" \
                    "h2o_feet,location=coyote_creek level\\ water_level=2 2"
        _request2 = "h2o_feet,location=coyote_creek level\\ water_level=3 3\n" \
                    "h2o_feet,location=coyote_creek level\\ water_level=4 4"

        self.assertEqual(_request1, _requests[0].parsed_body)
        self.assertEqual(_request2, _requests[1].parsed_body)
        pass

    def test_subscribe_wait(self):
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        self._write_client.write("my-bucket", "my-org", "h2o_feet,location=coyote_creek level\\ water_level=1 1")
        self._write_client.write("my-bucket", "my-org", "h2o_feet,location=coyote_creek level\\ water_level=2 2")

        time.sleep(1)

        _requests = httpretty.httpretty.latest_requests

        self.assertEqual(1, len(_requests))

        _request = "h2o_feet,location=coyote_creek level\\ water_level=1 1\n" \
                   "h2o_feet,location=coyote_creek level\\ water_level=2 2"

        self.assertEqual(_request, _requests[0].parsed_body)

    def test_batch_size_group_by(self):
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        self._write_client.write("my-bucket", "my-org",
                                 "h2o_feet,location=coyote_creek level\\ water_level=1 1")

        self._write_client.write("my-bucket", "my-org",
                                 "h2o_feet,location=coyote_creek level\\ water_level=2 2",
                                 write_precision=WritePrecision.S)

        self._write_client.write("my-bucket", "my-org-a",
                                 "h2o_feet,location=coyote_creek level\\ water_level=3 3")

        self._write_client.write("my-bucket", "my-org-a",
                                 "h2o_feet,location=coyote_creek level\\ water_level=4 4")

        self._write_client.write("my-bucket2", "my-org-a",
                                 "h2o_feet,location=coyote_creek level\\ water_level=5 5")

        self._write_client.write("my-bucket", "my-org-a",
                                 "h2o_feet,location=coyote_creek level\\ water_level=6 6")

        time.sleep(1)

        _requests = httpretty.httpretty.latest_requests

        self.assertEqual(5, len(_requests))

        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=1 1", _requests[0].parsed_body)
        self.assertEqual("ns", _requests[0].querystring["precision"][0])
        self.assertEqual("my-bucket", _requests[0].querystring["bucket"][0])

        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=2 2", _requests[1].parsed_body)
        self.assertEqual("s", _requests[1].querystring["precision"][0])
        self.assertEqual("my-bucket", _requests[1].querystring["bucket"][0])

        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=3 3\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=4 4", _requests[2].parsed_body)
        self.assertEqual("ns", _requests[2].querystring["precision"][0])
        self.assertEqual("my-bucket", _requests[2].querystring["bucket"][0])

        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=5 5", _requests[3].parsed_body)
        self.assertEqual("ns", _requests[3].querystring["precision"][0])
        self.assertEqual("my-bucket2", _requests[3].querystring["bucket"][0])

        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=6 6", _requests[4].parsed_body)
        self.assertEqual("ns", _requests[4].querystring["precision"][0])
        self.assertEqual("my-bucket", _requests[4].querystring["bucket"][0])

        pass

    def test_flush_interval(self):
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        self._write_client.write("my-bucket", "my-org",
                                 ["h2o_feet,location=coyote_creek level\\ water_level=1 1",
                                  "h2o_feet,location=coyote_creek level\\ water_level=2 2"])

        time.sleep(1)
        self.assertEqual(1, len(httpretty.httpretty.latest_requests))

        self._write_client.write("my-bucket", "my-org", "h2o_feet,location=coyote_creek level\\ water_level=3 3")

        time.sleep(2)

        self.assertEqual(1, len(httpretty.httpretty.latest_requests))

        time.sleep(3)

        self.assertEqual(2, len(httpretty.httpretty.latest_requests))

        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=3 3",
                         httpretty.httpretty.latest_requests[1].parsed_body)

    def test_jitter_interval(self):
        self._write_client.__del__()
        self._write_client = WriteApi(influxdb_client=self.influxdb_client,
                                      write_options=WriteOptions(batch_size=2, flush_interval=5_000,
                                                                 jitter_interval=3_000))

        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        self._write_client.write("my-bucket", "my-org",
                                 ["h2o_feet,location=coyote_creek level\\ water_level=1 1",
                                  "h2o_feet,location=coyote_creek level\\ water_level=2 2"])

        time.sleep(3)
        self.assertEqual(1, len(httpretty.httpretty.latest_requests))

        self._write_client.write("my-bucket", "my-org", "h2o_feet,location=coyote_creek level\\ water_level=3 3")

        time.sleep(2)

        self.assertEqual(1, len(httpretty.httpretty.latest_requests))

        time.sleep(6)

        self.assertEqual(2, len(httpretty.httpretty.latest_requests))

        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=3 3",
                         httpretty.httpretty.latest_requests[1].parsed_body)

    def test_retry_interval(self):

        self._write_client.__del__()

        # Set retry interval to 1_500
        self.write_options = WriteOptions(batch_size=2, flush_interval=5_000, retry_interval=1_500)
        self._write_client = WriteApi(influxdb_client=self.influxdb_client, write_options=self.write_options)

        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=503)
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=429,
                               adding_headers={'Retry-After': '3'})
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=503)

        self._write_client.write("my-bucket", "my-org",
                                 ["h2o_feet,location=coyote_creek level\\ water_level=1 1",
                                  "h2o_feet,location=coyote_creek level\\ water_level=2 2"])

        time.sleep(1)
        self.assertEqual(1, len(httpretty.httpretty.latest_requests), msg="first request immediately")

        time.sleep(1.5)
        self.assertEqual(2, len(httpretty.httpretty.latest_requests), msg="second request after delay_interval")

        time.sleep(3)
        self.assertEqual(3, len(httpretty.httpretty.latest_requests), msg="third request after Retry-After")

        time.sleep(37.5)
        self.assertEqual(4, len(httpretty.httpretty.latest_requests), msg="fourth after exponential delay = 1.5 * 5**2")

        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=1 1\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=2 2",
                         httpretty.httpretty.latest_requests[0].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=1 1\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=2 2",
                         httpretty.httpretty.latest_requests[1].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=1 1\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=2 2",
                         httpretty.httpretty.latest_requests[2].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=1 1\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=2 2",
                         httpretty.httpretty.latest_requests[3].parsed_body)

        pass

    def test_retry_interval_max_retries(self):
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=429,
                               adding_headers={'Retry-After': '1'})

        self._write_client.__del__()
        self._write_client = WriteApi(influxdb_client=self.influxdb_client,
                                      write_options=WriteOptions(batch_size=2, flush_interval=5_000, max_retries=5))

        self._write_client.write("my-bucket", "my-org",
                                 ["h2o_feet,location=coyote_creek level\\ water_level=1 1",
                                  "h2o_feet,location=coyote_creek level\\ water_level=2 2"])

        time.sleep(8)

        self.assertEqual(6, len(httpretty.httpretty.latest_requests))

    def test_recover_from_error(self):
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=400)

        self._write_client.write("my-bucket", "my-org",
                                 ["h2o_feet,location=coyote_creek",
                                  "h2o_feet,location=coyote_creek"])

        self._write_client.write("my-bucket", "my-org",
                                 ["h2o_feet,location=coyote_creek level\\ water_level=1 1",
                                  "h2o_feet,location=coyote_creek level\\ water_level=2 2"])

        time.sleep(1)

        _requests = httpretty.httpretty.latest_requests

        self.assertEqual(2, len(_requests))

        pass

    def test_record_types(self):
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        # Record item
        _record = "h2o_feet,location=coyote_creek level\\ water_level=1 1"
        self._write_client.write("my-bucket", "my-org", _record)

        # Point item
        _point = Point("h2o_feet").tag("location", "coyote_creek").field("level water_level", 2.0).time(2)
        self._write_client.write("my-bucket", "my-org", _point)

        # Record list
        self._write_client.write("my-bucket", "my-org",
                                 ["h2o_feet,location=coyote_creek level\\ water_level=3 3",
                                  "h2o_feet,location=coyote_creek level\\ water_level=4 4"])

        # Point list
        _point1 = Point("h2o_feet").tag("location", "coyote_creek").field("level water_level", 5.0).time(5)
        _point2 = Point("h2o_feet").tag("location", "coyote_creek").field("level water_level", 6.0).time(6)
        self._write_client.write("my-bucket", "my-org", [_point1, _point2])

        # Observable
        _recordObs = "h2o_feet,location=coyote_creek level\\ water_level=7 7"
        _pointObs = Point("h2o_feet").tag("location", "coyote_creek").field("level water_level", 8.0).time(8)

        self._write_client.write("my-bucket", "my-org", rx.of(_recordObs, _pointObs))

        _data = rx \
            .range(9, 13) \
            .pipe(ops.map(lambda i: "h2o_feet,location=coyote_creek level\\ water_level={0} {0}".format(i)))
        self._write_client.write("my-bucket", "my-org", _data)

        # Dictionary item
        _dict = {"measurement": "h2o_feet", "tags": {"location": "coyote_creek"},
                 "time": 13, "fields": {"level water_level": 13.0}}
        self._write_client.write("my-bucket", "my-org", _dict)

        # Dictionary list
        _dict1 = {"measurement": "h2o_feet", "tags": {"location": "coyote_creek"},
                  "time": 14, "fields": {"level water_level": 14.0}}
        _dict2 = {"measurement": "h2o_feet", "tags": {"location": "coyote_creek"},
                  "time": 15, "fields": {"level water_level": 15.0}}
        self._write_client.write("my-bucket", "my-org", [_dict1, _dict2])

        # Bytes item
        _bytes = "h2o_feet,location=coyote_creek level\\ water_level=16 16".encode("utf-8")
        self._write_client.write("my-bucket", "my-org", _bytes)

        # Bytes list
        _bytes1 = "h2o_feet,location=coyote_creek level\\ water_level=17 17".encode("utf-8")
        _bytes2 = "h2o_feet,location=coyote_creek level\\ water_level=18 18".encode("utf-8")
        self._write_client.write("my-bucket", "my-org", [_bytes1, _bytes2])

        # Tuple
        _bytes3 = "h2o_feet,location=coyote_creek level\\ water_level=19 19".encode("utf-8")
        _bytes4 = "h2o_feet,location=coyote_creek level\\ water_level=20 20".encode("utf-8")
        self._write_client.write("my-bucket", "my-org", (_bytes3, _bytes4, ))

        time.sleep(1)

        _requests = httpretty.httpretty.latest_requests

        self.assertEqual(10, len(_requests))

        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=1 1\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=2 2", _requests[0].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=3 3\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=4 4", _requests[1].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=5 5\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=6 6", _requests[2].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=7 7\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=8 8", _requests[3].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=9 9\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=10 10", _requests[4].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=11 11\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=12 12", _requests[5].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=13 13\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=14 14", _requests[6].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=15 15\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=16 16", _requests[7].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=17 17\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=18 18", _requests[8].parsed_body)
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=19 19\n"
                         "h2o_feet,location=coyote_creek level\\ water_level=20 20", _requests[9].parsed_body)

        pass

    def test_write_point_different_precision(self):
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        _point1 = Point("h2o_feet").tag("location", "coyote_creek").field("level water_level", 5.0) \
            .time(5, WritePrecision.S)
        _point2 = Point("h2o_feet").tag("location", "coyote_creek").field("level water_level", 6.0) \
            .time(6, WritePrecision.NS)

        self._write_client.write("my-bucket", "my-org", [_point1, _point2])

        time.sleep(1)

        _requests = httpretty.httpretty.latest_requests

        self.assertEqual(2, len(_requests))

        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=5 5", _requests[0].parsed_body)
        self.assertEqual("s", _requests[0].querystring["precision"][0])
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=6 6", _requests[1].parsed_body)
        self.assertEqual("ns", _requests[1].querystring["precision"][0])

    def test_write_result(self):
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        _record = "h2o_feet,location=coyote_creek level\\ water_level=1 1"
        _result = self._write_client.write("my-bucket", "my-org", _record)

        self.assertEqual(None, _result)

    def test_del(self):
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        _record = "h2o_feet,location=coyote_creek level\\ water_level=1 1"
        _result = self._write_client.write("my-bucket", "my-org", _record)

        self._write_client.__del__()

        _requests = httpretty.httpretty.latest_requests

        self.assertEqual(1, len(_requests))
        self.assertEqual("h2o_feet,location=coyote_creek level\\ water_level=1 1", _requests[0].parsed_body)

    def test_default_tags(self):
        self._write_client.__del__()

        self.id_tag = "132-987-655"
        self.customer_tag = "California Miner"

        self._write_client = WriteApi(influxdb_client=self.influxdb_client,
                                      write_options=WriteOptions(batch_size=1),
                                      point_settings=PointSettings(**{"id": self.id_tag,
                                                                      "customer": self.customer_tag}))

        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        _point1 = {"measurement": "h2o_feet", "tags": {"location": "coyote_creek"},
                   "time": "2009-11-10T22:00:00Z", "fields": {"water_level": 1.0}}

        _point_list = [_point1]

        self._write_client.write("my-bucket", "my-org", _point_list)

        time.sleep(1)

        requests = httpretty.httpretty.latest_requests
        self.assertEqual(1, len(requests))

        request = str(requests[0].body)
        self.assertNotEqual(-1, request.find('customer=California\\\\ Miner'))
        self.assertNotEqual(-1, request.find('id=132-987-655'))

    def test_user_agent_header(self):
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        self._write_client.write("my-bucket", "my-org",
                                 ["h2o_feet,location=coyote_creek level\\ water_level=1 1",
                                  "h2o_feet,location=coyote_creek level\\ water_level=2 2"])

        time.sleep(1)

        requests = httpretty.httpretty.latest_requests
        self.assertEqual(1, len(requests))
        self.assertEqual(f'influxdb-client-python/{influxdb_client.__version__}', requests[0].headers['User-Agent'])

    def test_to_low_flush_interval(self):

        self._write_client.__del__()
        self._write_client = WriteApi(influxdb_client=self.influxdb_client,
                                      write_options=WriteOptions(batch_size=8,
                                                                 flush_interval=1,
                                                                 jitter_interval=1000))

        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        for i in range(50):
            val_one = float(i)
            val_two = float(i) + 0.5
            point_one = Point("OneMillis").tag("sensor", "sensor1").field("PSI", val_one).time(time=i)
            point_two = Point("OneMillis").tag("sensor", "sensor2").field("PSI", val_two).time(time=i)

            self._write_client.write("my-bucket", "my-org", [point_one, point_two])
            time.sleep(0.1)

        self._write_client.__del__()

        _requests = httpretty.httpretty.latest_requests

        for _request in _requests:
            body = _request.parsed_body
            self.assertTrue(body, msg="Parsed body should be not empty " + str(_request))

        httpretty.reset()

    def test_batching_data_frame(self):
        from influxdb_client.extras import pd

        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)
        httpretty.register_uri(httpretty.POST, uri="http://localhost/api/v2/write", status=204)

        data_frame = pd.DataFrame(data=[["coyote_creek", 1.0], ["coyote_creek", 2.0],
                                        ["coyote_creek", 3.0], ["coyote_creek", 4.0]],
                                  index=[1, 2, 3, 4],
                                  columns=["location", "level water_level"])

        self._write_client.write("my-bucket", "my-org", record=data_frame,
                                 data_frame_measurement_name='h2o_feet',
                                 data_frame_tag_columns=['location'])

        time.sleep(1)

        _requests = httpretty.httpretty.latest_requests

        self.assertEqual(2, len(_requests))
        _request1 = "h2o_feet,location=coyote_creek level\\ water_level=1.0 1\n" \
                    "h2o_feet,location=coyote_creek level\\ water_level=2.0 2"
        _request2 = "h2o_feet,location=coyote_creek level\\ water_level=3.0 3\n" \
                    "h2o_feet,location=coyote_creek level\\ water_level=4.0 4"

        self.assertEqual(_request1, _requests[0].parsed_body)
        self.assertEqual(_request2, _requests[1].parsed_body)


if __name__ == '__main__':
    unittest.main()
