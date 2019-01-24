# Sanic MicroService Example
> Fork from https://github.com/songcser/sanic-ms

## Usage (@kevinqq)
[CHN version](https://www.jianshu.com/p/c3e34228f4fa) 

sanicms is treated as a 'framework' or 'module', you can create any services (apps) to use this module.

How to run:
1. use Docker
- git clone and cd into `sanic-ms`
- first run: `BUILD=y ./develop/reset.sh` or if you already built, just run: `./develop/reset.sh`

(add `"${PWD}/sanicms:/service/sanicms"` into `docker-compose.yml` volumes, otherwise docker-compose ERROR: `ModuleNotFoundError: No module named 'sanicms'`)

2. Manually run as solo app
- create you app in / dir (like: cp examples/user_service/* ./)
- run: python -m server

Note before you run 2):
- your default config is `settings.py`
- update your postgres db info
- `/sanicms/server.py`, modify import: `from sanic.response import json as sanic_json`. Otherwise error: 'module is not callable' because you run as module 'python -m server'?? or dup name of 'response'??

## Project structure
```
├── develop             # 开发脚本
│   ├── cluster.sh
│   ├── reset.sh        # 初始化项目
│   ├── test.sh
│   ├── utils.sh
│   ├── wait-for-it.sh
│   └── wait-service.sh
├── region_service      # 微服务之1
│   ├── sanicms
│   ├── info.log
│   ├── migrations.py
│   ├── models.py
│   ├── server.py
│   ├── settings.py
│   └── views.py
├── role_service        # 微服务之2
│   ├── ...
├── user_service        # 微服务之3
│   ├── ...
├── sanicms             # 微服务主框架
│   ├── __init__.py
│   ├── client.py
│   ├── config.py
│   ├── db.py
│   ├── doc.py
│   ├── exception.py
│   ├── loggers.py
│   ├── logging.yml
│   ├── __main__.py
│   ├── migrations.py
│   ├── openapi.py
│   ├── server.py
│   ├── service.py
│   ├── tests.py
│   └── utils.py
├── docker-compose-cluster.yml
├── docker-compose-service-cluster.yml
├── docker-compose.yml  # Docker微服务服务的配置文件，包括db/zipkin/swagger/consul
├── Dockerfile          # Docker微服务的基本环境包
├── pylintrc
├── README.md
└── requirements.txt    # Python依赖模块
```

## There's some update of Sanic 18.12.0 and you need to do some adaptions to bring this example up:
1. `develop/reset.sh`
	there's no "server", change it to "user_server", "role_server", "region_server"
	no "x_server" in the beginning, comment it out at 1st run

2. port 5432 is used by Host
	modify `docker-compose.yml`:
		services - db - ports "55432:5432"	# host:container

3. service response "AttributeError: 'str' object has no attribute 'output'"
	modify `service.py`: return response.text('user service')

4. run `./develop/reset.sh`
```
kevinqq@kevinqq-VB:~/git/sanic-ms/$ ./develop/reset.sh 
>>> removing existing services
No stopped containers
>>> starting db
Recreating examples_db_1 ... 
Recreating examples_db_1 ... done
trying to >>> connect postgres 1
/var/run/postgresql:5432 - accepting connections
>>> starting services
examples_swagger_1 is up-to-date
examples_zipkin_1 is up-to-date
examples_db_1 is up-to-date
Recreating examples_user_server_1 ... 
Recreating examples_region_server_1 ... 
Recreating examples_user_server_1
Recreating examples_role_server_1 ... 
Recreating examples_region_server_1
Recreating examples_role_server_1 ... done
>>> create tables
Starting examples_zipkin_1 ... done
Starting examples_db_1 ... done
Success Migration
Starting examples_zipkin_1 ... done
Starting examples_db_1 ... done
Success Migration
Starting examples_zipkin_1 ... done
Starting examples_db_1 ... done
Success Migration
```
check service is up or not:

```
kevinqq@kevinqq-VB:~/git/sanic-ms/examples$ docker-compose ps
          Name                        Command               State                       Ports                     
------------------------------------------------------------------------------------------------------------------
examples_consul1_1         docker-entrypoint.sh agent ...   Up      8300/tcp, 8301/tcp, 8301/udp, 8302/tcp,        
                                                                    8302/udp, 0.0.0.0:8500->8500/tcp, 8600/tcp,    
                                                                    8600/udp
examples_db_1              docker-entrypoint.sh postgres    Up      0.0.0.0:55432->5432/tcp                       
examples_region_server_1   python -m server                 Up      0.0.0.0:8050->8050/tcp                        
examples_role_server_1     python -m server                 Up      0.0.0.0:8020->8020/tcp                        
examples_swagger_1         sh /usr/share/nginx/docker ...   Up      0.0.0.0:8090->8080/tcp                        
examples_user_server_1     python -m server                 Up      0.0.0.0:8030->8030/tcp                        
examples_zipkin_1          /bin/sh -c test -n "$STORA ...   Up      0.0.0.0:9410->9410/tcp, 0.0.0.0:9411->9411/tcp

```
5. check logs
- docker-compose logs -f
- Now all the microservice services are up!
- view service: http://localhost:8020, http://localhost:8030, http://localhost:8050

6. consul 
- un-comment cosul of `docker-compose.yml`
- reset.sh
- access consul: http://localhost:8500/

7. swagger
- modify openapi address to user_service 8030
- reset.sh
- access swagger: http://localhost:8090/
- and you can switch different services by clicking "Explore": 8020, 8030, 8050


## how to inter-active Docker container:
docker run -ti sanic-ms_user_server sh


## ===================== original README ====================

## Enviroment
    We use docker and docker-compose to create the dev env automatically.
    
    Currently it contains three docker images.
	 
	 - "db" for Postgres
	 - "server" for Sanic server

## Install Docker & Docker-Compose
### Install Docker
[Docker For Mac](https://www.docker.com/docker-mac)

### Install Docker-Compose
```bash
(sudo) pip install -U docker-compose
```

### Registry-Mirror
[DaoCloud Mirror](https://www.daocloud.io/mirror)

## Pull Source Code
 ```bash
git clone https://github.com/songcser/sanic-ms
cd sanic-ms/examples
 ```

## Develop
### Pull and run docker container
```bash
BUILD=y PULL=y ./develop/reset.sh
```

### Reset
```bash
./develop/reset.sh
```

## Restart server service
```bash
docker-compose restart <server>
```

## Logs
```bash
docker-compose logs
```

### Server Logs
```bash
docker-compose logs -f <server>
```

## Cluster Service
```sh
./develop/cluster.sh
```

## Test

```
./develop/test.sh
```

## Access Server

```
open http://localhost:8000

open http://localhost:8000/users/
```

## Access API

```
open http://localhost:8090
```
![image](https://github.com/songcser/sanic-ms/raw/master/examples/images/1514528294957.jpg)

## Access Zipkin
```
open http://localhost:9411
```
![image](https://github.com/songcser/sanic-ms/raw/master/examples/images/1514528423339.jpg)
![image](https://github.com/songcser/sanic-ms/raw/master/examples/images/1514528479787.jpg)

## Access Consul
```
open http://192.168.99.100:8500/ui/#/dc1/services
```
![image](https://github.com/songcser/sanic-ms/raw/master/examples/images/1514528479788.jpg)
