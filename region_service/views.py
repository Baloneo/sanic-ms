import logging
import ujson
import datetime

from sanic import Blueprint

from sanicms import doc
from models import Province, City

region_bp = Blueprint('region', url_prefix='regions')

@region_bp.post('/provinces', name='add_provice')
@doc.summary('add provice')
@doc.description('add provice')
@doc.consumes(Province)
@doc.produces({'id': id})
async def add_provice(request):
    data = request['data']
    async with request.app.db.transaction(request) as cur:
        record = await cur.fetchrow(
            """ INSERT INTO provinces(name, create_time)
                VALUES($1, $2)
                RETURNING id
            """, data['name'], datetime.datetime.utcnow()
        )
        return {'id': record['id']}
    

@region_bp.get('/provinces/<id:int>', name='get_province')
@doc.summary('get province info')
@doc.produces(Province)
async def get_province(request, id):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(
            ''' SELECT * FROM provinces WHERE id = $1 ''', id
        )
        return records


@region_bp.post('/cities', name='add_city')
@doc.summary('add city')
@doc.description('add city')
@doc.consumes(City)
@doc.produces({'id': id})
async def add_city(request):
    data = request['data']
    async with request.app.db.transaction(request) as cur:
        record = await cur.fetchrow(
            """ INSERT INTO cities(name, province_id, create_time)
                VALUES($1, $2, $3)
                RETURNING id
            """, data['name'], data['province_id'], datetime.datetime.utcnow()
        )
        return {'id': record['id']}
    

@region_bp.get('/cities/<id:int>', name='get_city')
@doc.summary('get city info')
@doc.produces(City)
async def get_city(request, id):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(
            ''' SELECT * FROM cities WHERE id = $1 ''', id
        )
        return records
