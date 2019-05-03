import json

from aiohttp.web import json_response

from utils import *


async def signin(request):
    # get user creditals
    request_data = await request.json()
    if 'phone_number' not in request_data or 'password' not in request_data:
        return json_response({'error': 'Login and Password are required.'},
                             status=401)

    phone_number = request_data['phone_number']
    password = request_data['password']

    # check user in database
    conn = await request.app['db_pool'].acquire()
    cur = await conn.cursor()
    await cur.execute(f'''SELECT id, phone_number, password, salt FROM core_user WHERE
            phone_number='{phone_number}';''')

    async for result in cur:
        user_id, phone_number, db_password, salt = result
        if check_passwords(password, salt, db_password):
            break
    else:
        return json_response({'error': 'Login or Password are incorrect.'}, status=401)

    # create session in database
    token, refresh_token = create_tokens(user_id, expiration_time=25)

    # create session in redis
    session_id = generate_salt(32)
    data_store = json.dumps({'user_id': user_id, 'token': token, 'refresh_token': refresh_token})
    await request.app['redis_pool'].set(refresh_token, data_store)
    await request.app['redis_pool'].set(session_id, data_store)

    # return session token
    response = json_response({'token': token, 'refresh_token': refresh_token, 'session_id': session_id}, status=200)
    return response


async def signup(request):
    request_data = await request.json()

    if not all([field in request_data for field in ('phone_number', 'password',
                                                    'user_name', 'address', 'type')]):
        return json_response({'error': 'Login and Password are required.'},
                             status=401)

    phone_number = request_data['phone_number']
    password = request_data['password']
    user_name = request_data['user_name']
    address = request_data['address']
    user_type = request_data['type']

    # check user in database
    conn = await request.app['db_pool'].acquire()
    cur = await conn.cursor()
    await cur.execute(f'''SELECT id, phone_number, password, salt FROM core_user WHERE
                          phone_number='{request_data['phone_number']}';''')

    async for result in cur:
        return json_response({'error': 'User with this phone exists'}, status=401)

    # create user in database
    hash_password, salt = hash_pass(password)
    await cur.execute(f'''INSERT INTO core_user(phone_number, password, salt, user_name, type) VALUES('{phone_number}', 
                        '{hash_password}', '{salt}', '{user_name}', '{user_type}') RETURNING id;''')

    user_id = list(await cur.fetchone())[0]
    if user_type == 'CU':
        await cur.execute(f'''INSERT INTO core_customer(address, user_id) VALUES('{address}', '{user_id}')''')
    else:
        await cur.execute(f'''INSERT INTO core_courier(user_id) VALUES('{user_id}')''')

    token, refresh_token = create_tokens(user_id, expiration_time=25)

    # create session in redis
    session_id = generate_salt(32)
    data_store = json.dumps({'user_id': user_id, 'token': token, 'refresh_token': refresh_token})
    await request.app['redis_pool'].set(refresh_token, data_store)
    await request.app['redis_pool'].set(session_id, data_store)

    # return session token
    response = json_response({'token': token, 'refresh_token': refresh_token, 'session_id': session_id}, status=200)
    return response


async def refresh_token(request):
    request_data = await request.json()

    if 'refresh_token' not in request_data or 'session_id' not in request_data:
        return json_response({'error': 'Refresh token is required.'}, status=401)

    session_id = request_data['session_id']

    try:
        payload_refresh = decode_token(request_data['refresh_token'])
        redis_data = await request.app['redis_pool'].get(request_data['refresh_token'])
        redis_data = json.loads(redis_data)

        await request.app['redis_pool'].delete(request_data['refresh_token'])

        new_token, new_refresh_token = create_tokens(redis_data['user_id'])
        data_store = json.dumps({'user_id': redis_data['user_id'], 'token': new_token, 'refresh_token': new_refresh_token})

        await request.app['redis_pool'].set(refresh_token, data_store)
        await request.app['redis_pool'].set(session_id, data_store)

        return json_response({'token': new_token, 'refresh_token': new_refresh_token}, status=200)

    except Exception:
        return json_response({'error': 'Refresh token is expired or incorrect.'}, status=403)


async def get_tokens(request):
    if 'session_id' not in request.query:
        return json_response({'error': 'Session id is required.'}, status=401)

    session_id = request.query['session_id']

    redis_data = await request.app['redis_pool'].get(session_id)
    redis_data = json.loads(redis_data)

    if not redis_data:
        return json_response({'Session id is incorrect.'}, status=403)

    return json_response({'token': redis_data['token'], 'refresh_token': redis_data['refresh_token']}, status=200)
