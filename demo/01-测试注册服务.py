from sanic import Sanic
from sanic.response import json
import consul

app = Sanic(__name__)


@app.route('/')
def hello(request):
    return json({"msg": "hello world!"})


def register(server_name, ip, port):
    c = consul.Consul()  # 连接consul 服务器，默认是127.0.0.1，可用host参数指定host
    print(f"开始注册服务{server_name}")
    # check = consul.Check.tcp(ip, port, "10s")  # 健康检查的ip，端口，检查时间
    check = consul.Check.http("http://localhost:8000/", "10s")
    c.agent.service.register(server_name, f"{server_name}-{ip}-{port}",
                             address=ip, port=port, check=check)  # 注册服务部分
    print(f"注册服务{server_name}成功")


def unregister(server_name, ip, port):
    c = consul.Consul()
    print(f"开始退出服务{server_name}")
    c.agent.service.deregister(f'{server_name}-{ip}-{port}')


if __name__ == '__main__':
    register("zhouwen", '127.0.0.1', 8000)
    app.run(host="0.0.0.0", port=8000, debug=True)
