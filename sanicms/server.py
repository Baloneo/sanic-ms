#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import logging.config
import datetime
import yaml
import os
import opentracing

from collections import defaultdict
from basictracer import BasicTracer

from sanic import Sanic, config, response
from sanic.exceptions import RequestTimeout, NotFound

from sanicms import load_config
from sanicms.db import ConnectionPool
from sanicms.utils import *
from sanicms.loggers import AioReporter
from sanicms.openapi import blueprint as openapi_blueprint
from sanicms.service import ServiceManager, service_watcher

with open(os.path.join(os.path.dirname(__file__), 'logging.yml'), 'r') as f:
    logging.config.dictConfig(yaml.load(f))

config = load_config()
appid = config.get('APP_ID', __name__)
app = Sanic(appid, error_handler=CustomHandler())
app.config = config
app.blueprint(openapi_blueprint)


@app.listener('before_server_start')
async def before_server_start(app, loop):
    queue = asyncio.Queue()
    app.queue = queue
    loop.create_task(consume(queue, app))
    loop.create_task(service_watcher(app, loop))
    reporter = AioReporter(queue=queue)
    tracer = BasicTracer(recorder=reporter)
    tracer.register_required_propagators()
    opentracing.tracer = tracer
    app.db = await ConnectionPool(loop=loop).init(app.config['DB_CONFIG'])
    service = ServiceManager(loop=loop, host=app.config['CONSUL_AGENT_HOST'])
    services = await service.discovery_services()
    app.services = defaultdict(list)
    for name in services[1].keys():
        s = await service.discovery_service(name)
        app.services[name].extend(s)


@app.listener('after_server_start')
async def after_server_start(app, loop):
    service = ServiceManager(app.name, loop=loop, host=app.config['CONSUL_AGENT_HOST'])
    await service.register_service(port=app.config['PORT'])
    app.service = service


@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    await app.service.deregister()
    app.queue.join()


@app.middleware('request')
async def cros(request):
    config = request.app.config
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': config['ACCESS_CONTROL_ALLOW_ORIGIN'],
            'Access-Control-Allow-Headers': config['ACCESS_CONTROL_ALLOW_HEADERS'],
            'Access-Control-Allow-Methods': config['ACCESS_CONTROL_ALLOW_METHODS']
        }
        return response.son({'code': 0}, headers=headers)
    if request.method == 'POST' or request.method == 'PUT':
        request['data'] = request.json
    span = before_request(request)
    request['span'] = span


@app.middleware('response')
async def cors_res(request, rsp):
    config = request.app.config
    span = request['span'] if 'span' in request else None
    if rsp is None:
        return rsp
    result = {'code': 0}
    if not isinstance(rsp, response.HTTPResponse):
        if isinstance(rsp, tuple) and len(rsp) == 2:
            result.update({
                'data': rsp[0],
                'pagination': rsp[1]
            })
        else:
            result.update({'data': rsp})
        rsp = response.json(result)
        if span:
            span.set_tag('http.status_code', "200")
    if span:
        span.set_tag('component', request.app.name)
        span.finish()
    rsp.headers["Access-Control-Allow-Origin"] = config['ACCESS_CONTROL_ALLOW_ORIGIN']
    rsp.headers["Access-Control-Allow-Headers"] = config['ACCESS_CONTROL_ALLOW_HEADERS']
    rsp.headers["Access-Control-Allow-Methods"] = config['ACCESS_CONTROL_ALLOW_METHODS']
    return rsp


@app.exception(RequestTimeout)
def timeout(request, exception):
    return response.json({'message': 'Request Timeout'}, 408)


@app.exception(NotFound)
def notfound(request, exception):
    return response.json(
        {'message': 'Requested URL {} not found'.format(request.url)}, 404)
