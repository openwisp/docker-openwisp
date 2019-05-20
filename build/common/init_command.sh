#!/bin/sh
# OpenWISP common module init script

if [ "$MODULE_NAME" = 'dashboard' ]; then 
    python services_status.py database redis
    python manage.py migrate --noinput
    python load_init_data.py
    python manage.py collectstatic --noinput
else 
    python services_status.py database dashboard
fi

envsubst < uwsgi.conf.ini > uwsgi.ini
uwsgi --ini uwsgi.ini
