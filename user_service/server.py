from sanic import response

import logging

from views import user_bp

from sanicms.server import app
from sanicms.client import Client

logger = logging.getLogger('sanic')

# add blueprint
app.blueprint(user_bp)

@app.listener('before_server_start')
async def before_srver_start(app, loop):
    app.region_client = Client('region-service', app=app)	# service name is APP-ID
    app.role_client = Client('role-service', app=app)

@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    app.region_client.close()
    app.role_client.close()

@app.route("/")
async def index(request):
    return 'user service'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=app.config['PORT'], debug=True)
