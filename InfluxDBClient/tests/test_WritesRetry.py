import unittest

from urllib3 import HTTPResponse
from urllib3.exceptions import MaxRetryError

from influxdb_client.client.write.retry import WritesRetry


class TestWritesRetry(unittest.TestCase):
    def test_copy(self):
        retry = WritesRetry(jitter_interval=123, exponential_base=3, max_retry_delay=145)
        self.assertEqual(retry.jitter_interval, 123)
        self.assertEqual(retry.max_retry_delay, 145)
        self.assertEqual(retry.exponential_base, 3)
        self.assertEqual(retry.total, 10)

        retry = retry.increment()
        self.assertEqual(retry.jitter_interval, 123)
        self.assertEqual(retry.max_retry_delay, 145)
        self.assertEqual(retry.exponential_base, 3)
        self.assertEqual(retry.total, 9)

        retry = retry.increment()
        self.assertEqual(retry.jitter_interval, 123)
        self.assertEqual(retry.max_retry_delay, 145)
        self.assertEqual(retry.exponential_base, 3)
        self.assertEqual(retry.total, 8)

    def test_backoff(self):
        retry = WritesRetry(total=5, backoff_factor=1, max_retry_delay=550)
        self.assertEqual(retry.total, 5)
        self.assertEqual(retry.is_exhausted(), False)
        self.assertEqual(retry.get_backoff_time(), 0)

        retry = retry.increment()
        self.assertEqual(retry.total, 4)
        self.assertEqual(retry.is_exhausted(), False)
        self.assertEqual(retry.get_backoff_time(), 1)

        retry = retry.increment()
        self.assertEqual(retry.total, 3)
        self.assertEqual(retry.is_exhausted(), False)
        self.assertEqual(retry.get_backoff_time(), 5)

        retry = retry.increment()
        self.assertEqual(retry.total, 2)
        self.assertEqual(retry.is_exhausted(), False)
        self.assertEqual(retry.get_backoff_time(), 25)

        retry = retry.increment()
        self.assertEqual(retry.total, 1)
        self.assertEqual(retry.is_exhausted(), False)
        self.assertEqual(retry.get_backoff_time(), 125)

        retry = retry.increment()
        self.assertEqual(retry.total, 0)
        self.assertEqual(retry.is_exhausted(), False)
        self.assertEqual(retry.get_backoff_time(), 550)

        with self.assertRaises(MaxRetryError) as cm:
            retry.increment()
        exception = cm.exception

        self.assertEqual("too many error responses", exception.reason.args[0])

    def test_backoff_max(self):
        retry = WritesRetry(total=5, backoff_factor=1, max_retry_delay=15)\
            .increment()\
            .increment()\
            .increment()\
            .increment()\
            .increment()

        self.assertEqual(retry.get_backoff_time(), 15)

    def test_backoff_jitter(self):
        retry = WritesRetry(total=5, backoff_factor=4, jitter_interval=2).increment()

        self.assertEqual(retry.total, 4)
        self.assertEqual(retry.is_exhausted(), False)

        backoff_time = retry.get_backoff_time()
        self.assertGreater(backoff_time, 4)
        self.assertLessEqual(backoff_time, 6)

    def test_backoff_exponential_base(self):
        retry = WritesRetry(total=5, backoff_factor=2, exponential_base=2)

        retry = retry.increment()
        self.assertEqual(retry.get_backoff_time(), 2)

        retry = retry.increment()
        self.assertEqual(retry.get_backoff_time(), 4)

        retry = retry.increment()
        self.assertEqual(retry.get_backoff_time(), 8)

        retry = retry.increment()
        self.assertEqual(retry.get_backoff_time(), 16)

    def test_get_retry_after(self):
        response = HTTPResponse()
        response.headers.add('Retry-After', '5')

        retry = WritesRetry()
        self.assertEqual(retry.get_retry_after(response), 5)

    def test_get_retry_after_jitter(self):
        response = HTTPResponse()
        response.headers.add('Retry-After', '5')

        retry = WritesRetry(jitter_interval=2)
        retry_after = retry.get_retry_after(response)
        self.assertGreater(retry_after, 5)
        self.assertLessEqual(retry_after, 7)

    def test_is_retry(self):
        retry = WritesRetry(method_whitelist=["POST"])

        self.assertTrue(retry.is_retry("POST", 429, True))

    def test_is_retry_428(self):
        retry = WritesRetry(method_whitelist=["POST"])

        self.assertFalse(retry.is_retry("POST", 428, True))

    def test_is_retry_430(self):
        retry = WritesRetry(method_whitelist=["POST"])

        self.assertTrue(retry.is_retry("POST", 430, True))

    def test_is_retry_retry_after_header_is_not_required(self):
        retry = WritesRetry(method_whitelist=["POST"])

        self.assertTrue(retry.is_retry("POST", 429, False))

    def test_is_retry_respect_method(self):
        retry = WritesRetry(method_whitelist=["POST"])

        self.assertFalse(retry.is_retry("GET", 429, False))

    def test_logging(self):
        response = HTTPResponse(
            body='{"code":"too many requests","message":"org 04014de4ed590000 has exceeded limited_write plan limit"}')
        response.headers.add('Retry-After', '63')

        with self.assertLogs('influxdb_client.client.write.retry', level='WARNING') as cm:
            WritesRetry(total=5, backoff_factor=1, max_retry_delay=15) \
                .increment(response=response) \
                .increment(error=Exception("too many requests")) \
                .increment(url='http://localhost:9999')

        self.assertEqual("WARNING:influxdb_client.client.write.retry:The retriable error occurred during request. "
                         "Reason: 'org 04014de4ed590000 has exceeded limited_write plan limit'. Retry in 63s.",
                         cm.output[0])
        self.assertEqual("WARNING:influxdb_client.client.write.retry:The retriable error occurred during request. "
                         "Reason: 'too many requests'.",
                         cm.output[1])
        self.assertEqual("WARNING:influxdb_client.client.write.retry:The retriable error occurred during request. "
                         "Reason: 'Failed request to: http://localhost:9999'.",
                         cm.output[2])
