import os
from datetime import datetime

import redis
from flask import Flask, Response, request

app = Flask(__name__)

KEY = os.environ.get('WIREGUARD_UPDATER_KEY')
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_PASS = os.environ.get('REDIS_PASS')
REDIS_DATABASE = os.environ.get('REDIS_DB', 15)


def _trigger_configuration_update(vpn_id):
    redis_kwargs = {}
    if REDIS_PASS:
        redis_kwargs['password'] = REDIS_PASS
    if REDIS_PORT:
        redis_kwargs['port'] = REDIS_PORT
    unix_timestamp = int(datetime.now().timestamp())
    try:
        rs = redis.Redis(REDIS_HOST, db=REDIS_DATABASE, **redis_kwargs)
        rs.set(f'wg-{vpn_id}', unix_timestamp)
    except redis.RedisError as error:
        app.logger.error(error)
        return Response(status=500)
    return Response(status=200)


@app.route(os.environ.get('WIREGUARD_UPDATER_ENDPOINT'), methods=['POST'])
def update_vpn_config():
    if request.args.get('key') != KEY:
        return Response(status=403)
    if request.args.get('vpn_id') is None:
        return Response(status=400)
    return _trigger_configuration_update(
        vpn_id=request.args.get('vpn_id'),
    )


@app.route('/ping', methods=['GET'])
def ping():
    return Response(status=200)


if __name__ == '__main__':
    app.run()
