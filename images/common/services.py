#!/usr/bin/python3

import os
import sys
import time

from utils import uwsgi_curl


def database_status():
    try:
        psycopg2.connect(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'],
            sslmode=os.environ['DB_SSLMODE'],
            sslcert=os.environ['DB_SSLCERT'],
            sslkey=os.environ['DB_SSLKEY'],
            sslrootcert=os.environ['DB_SSLROOTCERT'],
        )
    except psycopg2.OperationalError:
        time.sleep(3)
        return False
    else:
        return True


def dashboard_status():
    try:
        uwsgi_curl(
            f"{os.environ['DASHBOARD_APP_SERVICE']}:{os.environ['DASHBOARD_APP_PORT']}"
        )
    except OSError:
        time.sleep(3)
        return False
    else:
        return True


def redis_status():
    rs = redis.Redis(os.environ['REDIS_HOST'])
    try:
        rs.ping()
    except redis.ConnectionError:
        time.sleep(3)
        return False
    else:
        return True


if __name__ == "__main__":
    arguments = sys.argv[1:]
    # Database Connection
    if "database" in arguments:
        import psycopg2

        print("Waiting for database to become available...")
        connected = False
        while not connected:
            connected = database_status()
        print("Connection with database established.")
    # OpenWISP Dashboard Connection
    if "dashboard" in arguments:
        print("Waiting for OpenWISP dashboard to become available...")
        connected = False
        while not connected:
            connected = dashboard_status()
        print("Connection with OpenWISP dashboard established.")
    # Redis Connection
    if "redis" in arguments:
        import redis

        print("Waiting for redis to become available...")
        connected = False
        while not connected:
            connected = redis_status()
        print("Connection with redis established.")
