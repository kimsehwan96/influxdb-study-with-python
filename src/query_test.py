from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

TOKEN = "sZr7ksaAkHQVBLIF7OGckgtoYaI358hSYupqeLUfxJRVAMCaJjidX-omUUWUeOV9YIm4kxUk8IYarkDFEb-cIw=="
org = "sehwan"
bucket = "testBucket"

client = InfluxDBClient(url="http://localhost:8086", token=TOKEN)

query_api = client.query_api()
query = 'from(bucket:"{}")\
|> range(start: -1m)\
|> filter(fn:(r) => r._measurement == "mem")\
|> filter(fn:(r) => r._field == "usage_percent" )'.format(bucket)
result = client.query_api().query(org=org, query=query)
# InfluxDBClient.query_api().query(..)의 리턴이 무엇인지 확인해보자!
#List[FluxTable]
#FluxTable 에 어떤 메소드가 있는지 확인해보자!


# class FluxTable(FluxStructure):
#     """A table is set of records with a common set of columns and a group key."""

#     def __init__(self) -> None:
#         """Initialize defaults."""
#         self.columns = []
#         self.records = []

#     def get_group_key(self):
#         """
#         Group key is a list of columns.

#         A table’s group key denotes which subset of the entire dataset is assigned to the table.
#         """
#         return list(filter(lambda column: (column.group is True), self.columns))

#     def __str__(self):
#         """Return formatted output."""
#         cls_name = type(self).__name__
#         return cls_name + "() columns: " + str(len(self.columns)) + ", records: " + str(len(self.records))

#     def __iter__(self):
#         """Iterate over records."""
#         return iter(self.records)

# 이친구다 ! 이친구는 colums와 records라는 속성이 있음 !
#FluxColumn 과 FluxRecord 객체는 무엇을 담고있을까?

# class FluxColumn(FluxStructure):
#     """A column has a label and a data type."""

#     def __init__(self, index=None, label=None, data_type=None, group=None, default_value=None) -> None:
#         """Initialize defaults."""
#         self.default_value = default_value
#         self.group = group
#         self.data_type = data_type
#         self.label = label
#         self.index = index

# FluxColumn 객체는 위와 같다.


# class FluxRecord(FluxStructure):
#     """A record is a tuple of named values and is represented using an object type."""

#     def __init__(self, table, values=None) -> None:
#         """Initialize defaults."""
#         if values is None:
#             values = {}
#         self.table = table
#         self.values = values

#     def get_start(self):
#         """Get '_start' value."""
#         return self["_start"]

#     def get_stop(self):
#         """Get '_stop' value."""
#         return self["_stop"]

#     def get_time(self):
#         """Get timestamp."""
#         return self["_time"]

#     def get_value(self):
#         """Get field value."""
#         return self["_value"]

#     def get_field(self):
#         """Get field name."""
#         return self["_field"]

#     def get_measurement(self):
#         """Get measurement name."""
#         return self["_measurement"]

#     def __getitem__(self, key):
#         """Get value by key."""
#         return self.values.__getitem__(key)

#     def __setitem__(self, key, value):
#         """Set value with key and value."""
#         return self.values.__setitem__(key, value)

#     def __str__(self):
#         """Return formatted output."""
#         cls_name = type(self).__name__
#         return cls_name + "() table: " + str(self.table) + ", " + str(self.values)

# FluxRecord는 위와 같다!