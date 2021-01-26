# CSV 데이터를 influxDB에 쓰기.

CSV파일을 DB에 쓰는 방법은 2가지가 있습니다. 하나는 Flux 언어를 쓰는 방법과
두번째는 CLI의 influx write 명령어를 쓰는것입니다.

## influx write 명령어
`influx write` 명령어를 이용해 CSV파일을 InfluxDB에 쓸 수 있습니다.   
이 때 신경써야 할 점은, 어떤 데이터가 어떤 용도인지 그저 `,`로 구분되기 때문에, 명령어에 --header 플래그를 추가해서 삽입하거나  
CSV파일의 상단에 어노테이션을 달아주어야 합니다. 우리는 어노테이션을 달아서 넣어보겠습니다.

`influx write -b example-bucket -f path/to/example.csv`

- exmaple.csv

```text
#datatype measurement,tag,double,dateTime:RFC3339
m,host,used_percent,time
mem,host1,64.23,2020-01-01T00:00:00Z
mem,host2,72.01,2020-01-01T00:00:00Z
mem,host1,62.61,2020-01-01T00:00:10Z
mem,host2,72.98,2020-01-01T00:00:10Z
mem,host1,63.40,2020-01-01T00:00:20Z
mem,host2,73.77,2020-01-01T00:00:20Z
```

