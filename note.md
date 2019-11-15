# consul
```bash
docker run -d -p 8500:8500 consul consul agent -data-dir=/consul/data -config-dir=/consul/config -dev -client=0.0.0.0 -bind=0.0.0.0
```
`docker run -d -p 8500:8500 consul consul` 表示运行consul容器