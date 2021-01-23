import unittest
from io import BytesIO

from urllib3 import HTTPResponse

from influxdb_client.client.flux_csv_parser import FluxCsvParser, FluxSerializationMode, FluxQueryException


class FluxCsvParserTest(unittest.TestCase):

    def test_one_table(self):
        data = "#datatype,string,long,dateTime:RFC3339,dateTime:RFC3339,string,string,string,string,long,long,string\n" \
               "#group,false,false,true,true,true,true,true,true,false,false,false\n" \
               "#default,_result,,,,,,,,,,\n" \
               ",result,table,_start,_stop,_field,_measurement,host,region,_value2,value1,value_str\n" \
               ",,0,1677-09-21T00:12:43.145224192Z,2018-07-16T11:21:02.547596934Z,free,mem,A,west,121,11,test\n"

        tables = self._parse_to_tables(data=data)
        self.assertEqual(1, tables.__len__())
        self.assertEqual(11, tables[0].columns.__len__())
        self.assertEqual(1, tables[0].records.__len__())

    def test_more_tables(self):
        data = "#datatype,string,long,dateTime:RFC3339,dateTime:RFC3339,string,string,string,string,long,long,string\n" \
               "#group,false,false,true,true,true,true,true,true,false,false,false\n" \
               "#default,_result,,,,,,,,,,\n" \
               ",result,table,_start,_stop,_field,_measurement,host,region,_value2,value1,value_str\n" \
               ",,0,1677-09-21T00:12:43.145224192Z,2018-07-16T11:21:02.547596934Z,free,mem,A,west,121,11,test\n" \
               ",,1,1677-09-21T00:12:43.145224192Z,2018-07-16T11:21:02.547596934Z,free,mem,B,west,484,22,test\n" \
               ",,2,1677-09-21T00:12:43.145224192Z,2018-07-16T11:21:02.547596934Z,usage_system,cpu,A,west,1444,38,test\n" \
               ",,3,1677-09-21T00:12:43.145224192Z,2018-07-16T11:21:02.547596934Z,user_usage,cpu,A,west,2401,49,test"

        tables = self._parse_to_tables(data=data)
        self.assertEqual(4, tables.__len__())
        self.assertEqual(11, tables[0].columns.__len__())
        self.assertEqual(1, tables[0].records.__len__())
        self.assertEqual(11, tables[1].columns.__len__())
        self.assertEqual(1, tables[1].records.__len__())
        self.assertEqual(11, tables[2].columns.__len__())
        self.assertEqual(1, tables[2].records.__len__())
        self.assertEqual(11, tables[3].columns.__len__())
        self.assertEqual(1, tables[3].records.__len__())

    def test_multiple_queries(self):
        data = "#datatype,string,long,string,string,dateTime:RFC3339,dateTime:RFC3339,dateTime:RFC3339,double,string\n" \
               "#group,false,false,true,true,true,true,false,false,true\n" \
               "#default,t1,,,,,,,,\n" \
               ",result,table,_field,_measurement,_start,_stop,_time,_value,tag\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:20:00Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:21:40Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:23:20Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:25:00Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:26:40Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:28:20Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:30:00Z,2,test1\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:20:00Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:21:40Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:23:20Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:25:00Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:26:40Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:28:20Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:30:00Z,2,test2\n" \
               "\n" \
               "#datatype,string,long,string,string,dateTime:RFC3339,dateTime:RFC3339,dateTime:RFC3339,double,string\n" \
               "#group,false,false,true,true,true,true,false,false,true\n" \
               "#default,t2,,,,,,,,\n" \
               ",result,table,_field,_measurement,_start,_stop,_time,_value,tag\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:20:00Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:21:40Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:23:20Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:25:00Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:26:40Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:28:20Z,2,test1\n" \
               ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:30:00Z,2,test1\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:20:00Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:21:40Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:23:20Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:25:00Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:26:40Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:28:20Z,2,test2\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:30:00Z,2,test2"

        tables = self._parse_to_tables(data=data)
        self.assertEqual(4, tables.__len__())
        self.assertEqual(9, tables[0].columns.__len__())
        self.assertEqual(7, tables[0].records.__len__())
        self.assertEqual(9, tables[1].columns.__len__())
        self.assertEqual(7, tables[1].records.__len__())
        self.assertEqual(9, tables[2].columns.__len__())
        self.assertEqual(7, tables[2].records.__len__())
        self.assertEqual(9, tables[3].columns.__len__())
        self.assertEqual(7, tables[3].records.__len__())

    def test_table_index_not_start_at_zero(self):
        data = "#datatype,string,long,string,string,dateTime:RFC3339,dateTime:RFC3339,dateTime:RFC3339,double,string\n" \
               "#group,false,false,true,true,true,true,false,false,true\n" \
               "#default,t1,,,,,,,,\n" \
               ",result,table,_field,_measurement,_start,_stop,_time,_value,tag\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:20:00Z,2,test1\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:21:40Z,2,test1\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:23:20Z,2,test1\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:25:00Z,2,test1\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:26:40Z,2,test1\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:28:20Z,2,test1\n" \
               ",,1,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:30:00Z,2,test1\n" \
               ",,2,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:20:00Z,2,test2\n" \
               ",,2,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:21:40Z,2,test2\n" \
               ",,2,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:23:20Z,2,test2\n" \
               ",,2,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:25:00Z,2,test2\n" \
               ",,2,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:26:40Z,2,test2\n" \
               ",,2,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:28:20Z,2,test2\n" \
               ",,2,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:30:00Z,2,test2\n"

        tables = self._parse_to_tables(data=data)
        self.assertEqual(2, tables.__len__())
        self.assertEqual(9, tables[0].columns.__len__())
        self.assertEqual(7, tables[0].records.__len__())
        self.assertEqual(9, tables[1].columns.__len__())
        self.assertEqual(7, tables[1].records.__len__())

    def test_response_with_error(self):
        data = "#datatype,string,long,string,string,dateTime:RFC3339,dateTime:RFC3339,dateTime:RFC3339,double,string\n" \
                 "#group,false,false,true,true,true,true,false,false,true\n" \
                 "#default,t1,,,,,,,,\n" \
                 ",result,table,_field,_measurement,_start,_stop,_time,_value,tag\n" \
                 ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:20:00Z,2,test1\n" \
                 ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:21:40Z,2,test1\n" \
                 ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:23:20Z,2,test1\n" \
                 ",,0,value,python_client_test,2010-02-27T04:48:32.752600083Z,2020-02-27T16:48:32.752600083Z,2020-02-27T16:25:00Z,2,test1\n" \
                 "\n" \
                 "#datatype,string,string\n" \
                 "#group,true,true\n" \
                 "#default,,\n" \
                 ",error,reference\n" \
                 ",\"engine: unknown field type for value: xyz\","

        with self.assertRaises(FluxQueryException) as cm:
            self._parse_to_tables(data=data)
        exception = cm.exception

        self.assertEqual('engine: unknown field type for value: xyz', exception.message)
        self.assertEqual('', exception.reference)

    def test_ParseExportFromUserInterface(self):

        data = "#group,false,false,true,true,true,true,true,true,false,false\n" \
           + "#datatype,string,long,dateTime:RFC3339,dateTime:RFC3339,string,string,string,string,double,dateTime:RFC3339\n" \
           + "#default,mean,,,,,,,,,\n" \
           + ",result,table,_start,_stop,_field,_measurement,city,location,_value,_time\n" \
           + ",,0,1754-06-26T11:30:27.613654848Z,2040-10-27T12:13:46.485Z,temperatureC,weather,London,us-midwest,30,1975-09-01T16:59:54.5Z\n" \
           + ",,1,1754-06-26T11:30:27.613654848Z,2040-10-27T12:13:46.485Z,temperatureF,weather,London,us-midwest,86,1975-09-01T16:59:54.5Z\n";

        tables = self._parse_to_tables(data=data)
        self.assertEqual(2, tables.__len__())
        self.assertEqual(1, tables[0].records.__len__())
        self.assertEqual(1, tables[1].records.__len__())
        self.assertFalse(tables[1].columns[0].group)
        self.assertFalse(tables[1].columns[1].group)
        self.assertTrue(tables[1].columns[2].group)

    @staticmethod
    def _parse_to_tables(data: str):
        fp = BytesIO(str.encode(data))
        _parser = FluxCsvParser(response=HTTPResponse(fp, preload_content=False),
                                serialization_mode=FluxSerializationMode.tables)
        list(_parser.generator())
        tables = _parser.tables
        return tables
