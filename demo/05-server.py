from sanic import Sanic
from sanic.response import json
import consul

app = Sanic(__name__)


@app.route('/')
def hello(request):
    return json({"msg": "hello world!"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)
