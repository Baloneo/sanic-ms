from sanic import Sanic, response
from sanic.response import json

import aiohttp
import aiozipkin as az

"""
integrate aiohttp to Sanic app, doc(CHN): https://www.jianshu.com/p/17bc4518b243
"""

host = '127.0.0.1'
port = 8000
zipkin_address = 'http://127.0.0.1:9411/api/v2/spans'

app = Sanic(__name__)
endpoint = az.create_endpoint('sanic_app', ipv4=host, port=port)

@app.listener('before_server_start')
async def init(app, loop):
    tracer = await az.create(zipkin_address, endpoint, sample_rate=1.0)
    trace_config = az.make_trace_config(tracer)
    app.aiohttp_session = aiohttp.ClientSession(trace_configs=[trace_config], loop=loop)
    app.tracer = tracer

@app.listener('after_server_stop')
def finish(app, loop):
    loop.run_until_complete(app.aiohttp_session.close())
    loop.close()

@app.route("/")
async def test(request):
    request['aiozipkin_span'] = request
    with app.tracer.new_trace() as span:
        span.name(f'HTTP {request.method} {request.path}')
        print(span)
        url = "https://www.163.com"
        with app.tracer.new_child(span.context) as span_producer:
            span_producer.kind(az.PRODUCER)
            span_producer.name('produce event click')
        return response.text('ok')

def request_span(request):
    with app.tracer.new_trace() as span:
        span.name(f'HTTP {request.method} {request.path}')
        kwargs = {
            'http.path':request.path,
            'http.method':request.method,
            'http.path':request.path,
            'http.route':request.url,
            'peer.ip':request.remote_addr or request.ip,
            'peer.port':request.port,
        }
        [span.tag(k, v) for k,v in kwargs.items()]
        span.kind(az.SERVER)
        return span

@app.route("/2")
async def tes2(request):
    request['aiozipkin_span'] = request
    span = request_span(request)
    with app.tracer.new_child(span.context) as span_producer:
        span_producer.kind(az.PRODUCER)
        span_producer.name('produce event click')
    return response.text('ok')

if __name__ == '__main__':        
    app.run(host="0.0.0.0", port=port, debug=True)
