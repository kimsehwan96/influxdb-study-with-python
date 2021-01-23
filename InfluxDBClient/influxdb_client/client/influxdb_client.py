"""InfluxDBClient is client for API defined in https://github.com/influxdata/influxdb/blob/master/http/swagger.yml."""

from __future__ import absolute_import

import configparser #인자 파싱을 위해서
import os

from influxdb_client import Configuration, ApiClient, HealthCheck, HealthService, Ready, ReadyService
from influxdb_client.client.authorizations_api import AuthorizationsApi
from influxdb_client.client.bucket_api import BucketsApi
from influxdb_client.client.delete_api import DeleteApi
from influxdb_client.client.labels_api import LabelsApi
from influxdb_client.client.organizations_api import OrganizationsApi
from influxdb_client.client.query_api import QueryApi
from influxdb_client.client.tasks_api import TasksApi
from influxdb_client.client.users_api import UsersApi
from influxdb_client.client.write_api import WriteApi, WriteOptions, PointSettings


class InfluxDBClient(object):
    """InfluxDBClient is client for InfluxDB v2."""

    def __init__(self, url, token, debug=None, timeout=10000, enable_gzip=False, org: str = None,
                 default_tags: dict = None, **kwargs) -> None:
        #생성자로 url, token은 디폴트값이 없으며, 그 외 args들은 모두 디폴트 값이 있음.
        #kwargs로는 다음과 같은 것들이 있음. verify_ssl, proxy, retries (urllib3.util.retry.Retry객체)
        """
        Initialize defaults.

        :param url: InfluxDB server API url (ex. http://localhost:8086).
        :param token: auth token
        :param debug: enable verbose logging of http requests
        :param timeout: default http client timeout
        :param enable_gzip: Enable Gzip compression for http requests. Currently only the "Write" and "Query" endpoints
                            supports the Gzip compression.
        :param org: organization name (used as a default in query and write API)
        :key bool verify_ssl: Set this to false to skip verifying SSL certificate when calling API from https server.
        :key str ssl_ca_cert: Set this to customize the certificate file to verify the peer.
        :key str proxy: Set this to configure the http proxy to be used (ex. http://localhost:3128)
        :key urllib3.util.retry.Retry retries: Set the default retry strategy that is used for all HTTP requests
                                               except batching writes. As a default there is no one retry strategy.

        """
        self.url = url
        self.token = token
        self.timeout = timeout
        self.org = org

        self.default_tags = default_tags

        conf = _Configuration()
        if self.url.endswith("/"):
            conf.host = self.url[:-1] #맨 마지막에 /가 들어올 경우 /를 제거한 문자열을 conf.host에 담는 로직
        else:
            conf.host = self.url
        conf.enable_gzip = enable_gzip
        conf.debug = debug
        conf.verify_ssl = kwargs.get('verify_ssl', True) #아래 세 인자는 kwargs이기 때문에 이렇게 파싱하며, 디폴트 값이 있다.
        conf.ssl_ca_cert = kwargs.get('ssl_ca_cert', None)
        conf.proxy = kwargs.get('proxy', None)

        auth_token = self.token
        auth_header_name = "Authorization" #아마 request 보낼떄의 헤더이름을 이렇게 작성한듯.
        auth_header_value = "Token " + auth_token #헤더에 들어가는 값을 Token foobarbaz 와 같이 담아서 보내는듯

        retries = kwargs.get('retries', False)

        self.api_client = ApiClient(configuration=conf, header_name=auth_header_name,
                                    header_value=auth_header_value, retries=retries) #InfluxDBClient 밑에 ApiClient 객체도 들고있음

    @classmethod #클래스메서드로 첫번째 인자를 cls를 받음
    def from_config_file(cls, config_file: str = "config.ini", debug=None, enable_gzip=False):
        """
        Configure client via '*.ini' file in segment 'influx2'.

        Supported options:
            - url
            - org
            - token
            - timeout,
            - verify_ssl
            - ssl_ca_cert
        """
        config = configparser.ConfigParser()
        config.read(config_file)

        url = config['influx2']['url']
        token = config['influx2']['token']

        timeout = None

        if config.has_option('influx2', 'timeout'):
            timeout = config['influx2']['timeout']

        org = None

        if config.has_option('influx2', 'org'):
            org = config['influx2']['org']

        verify_ssl = True
        if config.has_option('influx2', 'verify_ssl'):
            verify_ssl = config['influx2']['verify_ssl']

        ssl_ca_cert = None
        if config.has_option('influx2', 'ssl_ca_cert'):
            ssl_ca_cert = config['influx2']['ssl_ca_cert']

        default_tags = None

        if config.has_section('tags'):
            default_tags = dict(config.items('tags'))

        if timeout:
            return cls(url, token, debug=debug, timeout=int(timeout), org=org, default_tags=default_tags,
                       enable_gzip=enable_gzip, verify_ssl=_to_bool(verify_ssl), ssl_ca_cert=ssl_ca_cert)

        return cls(url, token, debug=debug, org=org, default_tags=default_tags, enable_gzip=enable_gzip,
                   verify_ssl=_to_bool(verify_ssl), ssl_ca_cert=ssl_ca_cert)

    @classmethod
    def from_env_properties(cls, debug=None, enable_gzip=False):
        """
        Configure client via environment properties.

        Supported environment properties:
            - INFLUXDB_V2_URL
            - INFLUXDB_V2_ORG
            - INFLUXDB_V2_TOKEN
            - INFLUXDB_V2_TIMEOUT
            - INFLUXDB_V2_VERIFY_SSL
            - INFLUXDB_V2_SSL_CA_CERT
        """
        url = os.getenv('INFLUXDB_V2_URL', "http://localhost:8086")
        token = os.getenv('INFLUXDB_V2_TOKEN', "my-token")
        timeout = os.getenv('INFLUXDB_V2_TIMEOUT', "10000")
        org = os.getenv('INFLUXDB_V2_ORG', "my-org")
        verify_ssl = os.getenv('INFLUXDB_V2_VERIFY_SSL', "True")
        ssl_ca_cert = os.getenv('INFLUXDB_V2_SSL_CA_CERT', None)

        default_tags = dict()

        for key, value in os.environ.items():
            if key.startswith("INFLUXDB_V2_TAG_"):
                default_tags[key[16:].lower()] = value

        return cls(url, token, debug=debug, timeout=int(timeout), org=org, default_tags=default_tags,
                   enable_gzip=enable_gzip, verify_ssl=_to_bool(verify_ssl), ssl_ca_cert=ssl_ca_cert)

    #write api 메서드가 여기있네. 얘는 WriteApi라는 객체를 리턴해주는 메서드임! 이런식으로 특정 객체를 리턴해주면 뒤에 명시적으로 리턴값 형태 써주는게 편한게 맞나봄!
    def write_api(self, write_options=WriteOptions(), point_settings=PointSettings()) -> WriteApi:
        """
        Create a Write API instance.

        :param point_settings:
        :param write_options: write api configuration
        :return: write api instance
        """
        #WriteApi 객체를 생성해서 리턴하는것임. 인자로 받는 write_options와 point_settings 모두 클래스네. 원형을 하나만 찾아보자!

        """
class WriteOptions(object):
    def __init__(self, write_type: WriteType = WriteType.batching,
                 batch_size=1_000, flush_interval=1_000,
                 jitter_interval=0,
                 retry_interval=5_000,
                 max_retries=3,
                 max_retry_delay=180_000,
                 exponential_base=5,
                 write_scheduler=ThreadPoolScheduler(max_workers=1)) -> None:
        self.write_type = write_type
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.jitter_interval = jitter_interval
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.max_retry_delay = max_retry_delay
        self.exponential_base = exponential_base
        self.write_scheduler = write_scheduler
        """
        # 보면 위 객체는 그냥 값들만 담고있음. 그니까 어떻게보면 javascript식 객체생성을 하는 느낌이네.
        return WriteApi(influxdb_client=self, write_options=write_options, point_settings=point_settings)

    def query_api(self) -> QueryApi: #QueryApi 객체를 리턴해줌
        """
        Create a Query API instance.

        :return: Query api instance
        """
        return QueryApi(self)

    def close(self):
        """Shutdown the client."""
        self.__del__() # 소멸자를 호출해서 셧다운하네

    def __del__(self):
        """Shutdown the client."""
        if self.api_client:
            self.api_client.__del__()
            self.api_client = None
    # 소멸자를 오버라이딩해서 커스텀 구현을 한것임

    def buckets_api(self) -> BucketsApi:
        """
        Create the Bucket API instance.

        :return: buckets api
        """
        return BucketsApi(self)

    def authorizations_api(self) -> AuthorizationsApi:
        """
        Create the Authorizations API instance.

        :return: authorizations api
        """
        return AuthorizationsApi(self)

    def users_api(self) -> UsersApi:
        """
        Create the Users API instance.

        :return: users api
        """
        return UsersApi(self)

    def organizations_api(self) -> OrganizationsApi:
        """
        Create the Organizations API instance.

        :return: organizations api
        """
        return OrganizationsApi(self)

    def tasks_api(self) -> TasksApi:
        """
        Create the Tasks API instance.

        :return: tasks api
        """
        return TasksApi(self)

    def labels_api(self) -> LabelsApi:
        """
        Create the Labels API instance.

        :return: labels api
        """
        return LabelsApi(self)

    def health(self) -> HealthCheck:
        """
        Get the health of an instance.

        :return: HealthCheck
        """
        health_service = HealthService(self.api_client)

        try:
            health = health_service.get_health()
            return health
        except Exception as e:
            return HealthCheck(name="influxdb", message=str(e), status="fail")

    def ready(self) -> Ready:
        """
        Get The readiness of the InfluxDB 2.0.

        :return: Ready
        """
        ready_service = ReadyService(self.api_client)
        return ready_service.get_ready()

    def delete_api(self) -> DeleteApi:
        """
        Get the delete metrics API instance.

        :return: delete api
        """
        return DeleteApi(self)


class _Configuration(Configuration):
    def __init__(self):
        Configuration.__init__(self)
        self.enable_gzip = False

    def update_request_header_params(self, path: str, params: dict):
        super().update_request_header_params(path, params)
        if self.enable_gzip:
            # GZIP Request
            if path == '/api/v2/write':
                params["Content-Encoding"] = "gzip"
                params["Accept-Encoding"] = "identity"
                pass
            # GZIP Response
            if path == '/api/v2/query':
                # params["Content-Encoding"] = "gzip"
                params["Accept-Encoding"] = "gzip"
                pass
            pass
        pass

    def update_request_body(self, path: str, body):
        _body = super().update_request_body(path, body)
        if self.enable_gzip:
            # GZIP Request
            if path == '/api/v2/write':
                import gzip
                if isinstance(_body, bytes):
                    return gzip.compress(data=_body)
                else:
                    return gzip.compress(bytes(_body, "utf-8"))

        return _body


def _to_bool(verify_ssl):
    return str(verify_ssl).lower() in ("yes", "true")
#verify_ssl 옵션을 파싱하기 위한 함수