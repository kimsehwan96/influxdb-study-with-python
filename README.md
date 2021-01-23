# TSDB (Time Series DataBase) 중 하나인 influx db


## 설치법

### in MacOS without Docker

- UI 있는 버전

https://dl.influxdata.com/influxdb/releases/influxdb2-2.0.3_darwin_amd64.tar.gz
위 링크를 클릭해 다운로드
```
tar zxvf influxdb2-2.0.3_darwin_amd64.tar.gz
```

- 압축 해제 이후 influx와 influxd를 특정 경로로 보내주어야 한다.
- `sudo cp sudo cp influxdb2.0.3_darwin_amd64/{influx,influxd} /usr/local/bin/`

- 저 경로로 보내주면 mac 터미널에서 influx, influxd 와 같은 경로를 명시하지 않고도 두 바이너리 실행 가능하다~!


### Install With Docker

- `docker run --name influxdb -p 8086:8086 quay.io/influxdb/influxdb:v2.0.3`
- 마지막 태그를 자신이 원하는 버전으로 사용하면 됨.
- influex 컨테이너 안으로 들어가기 위해서는
- `docker exec -it influxdb /bin/bash`


## 초기 설정!! 

![1](images/1.png)

- 최초 진입 화면(`localhost:8086`)

![2](images/2.png)

- UI 기반으로 최초 설정을 진행 할 수 있다.
- CLI 기반으로도 설정 가능!

- 최초 설정은 다음과 같은 것들을 설정하는 것임
    - 디폴트 조직
    - 디폴트 유저
    - 디폴트 버킷
    - 관리자 인증 토큰

- 최초 설정을 하면서 만들어진 관리자 토큰 (Admin token)은 해당 인플럭스DB의 모든 조직에 대해서 모든 읽기, 쓰기 권한을 갖고있다.
- 따라서 조직간 충돌을 방지하기 위해서 각 조직마다 All Access Token을 생성하여 각 조직별 관리자 토큰을 생성하는 것을 권장함!
- 추후 작성하기로 하며 개발 단계에서는 패스

![3](images/3.png)

- 최초 셋업 설정

