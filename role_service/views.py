import logging
import ujson

from sanic import Blueprint, response

from sanicms import doc
from models import Role

role_bp = Blueprint('role', url_prefix='roles')


@role_bp.post('/', name='add_role')
@doc.summary('add role')
@doc.description('add role')
@doc.consumes(Role)
@doc.produces({'id': id})
async def add_role(request):
    data = request['data']
    async with request.app.db.transaction(request) as cur:
        record = await cur.fetchrow(
            """ INSERT INTO roles(name)
                VALUES($1)
                RETURNING id
            """, data['name']
        )
        return {'id': record['id']}

@role_bp.get('/', name='get_roles')
@doc.summary('get roles')
@doc.produces(Role)
async def get_roles(request):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(
            ''' SELECT * FROM roles '''
        )
        return records    

@role_bp.get('/<id:int>', name='get_role')
@doc.summary('get role by id')
@doc.produces(Role)
async def get_role(request, id):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(
            ''' SELECT * FROM roles WHERE id = $1 ''', id
        )
        return records
