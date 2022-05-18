import os

from celery import Celery
from celery.schedules import crontab
from django.utils.timezone import timedelta
from openwisp.utils import env_bool

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openwisp.settings')

radius_schedule, topology_schedule, monitoring_schedule = {}, {}, {}
task_routes = {}

if env_bool(os.environ.get('USE_OPENWISP_CELERY_NETWORK')):
    task_routes['openwisp_controller.connection.tasks.*'] = {'queue': 'network'}

if env_bool(os.environ.get('USE_OPENWISP_MONITORING')):
    monitoring_schedule = {
        'run_checks': {
            'task': 'openwisp_monitoring.check.tasks.run_checks',
            'schedule': timedelta(minutes=5),
        },
    }
    if env_bool(os.environ.get('USE_OPENWISP_CELERY_MONITORING')):
        task_routes['openwisp_monitoring.check.tasks.perform_check'] = {
            'queue': 'monitoring_checks'
        }
        task_routes['openwisp_monitoring.monitoring.tasks.*'] = {'queue': 'monitoring'}

if env_bool(os.environ.get('USE_OPENWISP_FIRMWARE')) and env_bool(
    os.environ.get('USE_OPENWISP_CELERY_FIRMWARE')
):
    task_routes['openwisp_firmware_upgrader.tasks.upgrade_firmware'] = {
        'queue': 'firmware_upgrader'
    }
    task_routes['openwisp_firmware_upgrader.tasks.batch_upgrade_operation'] = {
        'queue': 'firmware_upgrader'
    }

if env_bool(os.environ.get('USE_OPENWISP_RADIUS')):
    radius_schedule = {
        'radius-periodic-tasks': {
            'task': 'openwisp.tasks.radius_tasks',
            'schedule': crontab(minute=30, hour=3),
            'args': (),
        },
    }

if env_bool(os.environ.get('USE_OPENWISP_TOPOLOGY')):
    topology_schedule = {
        'topology-snapshot-tasks': {
            'task': 'openwisp.tasks.save_snapshot',
            'schedule': crontab(minute=45, hour=23),
            'args': (),
        },
        'topology-periodic-tasks': {
            'task': 'openwisp.tasks.update_topology',
            'schedule': crontab(minute='*/5'),
            'args': (),
        },
    }

notification_schedule = {
    'notification-delete-tasks': {
        'task': 'openwisp_notifications.tasks.delete_old_notifications',
        'schedule': crontab(minute=00, hour=23),
        'args': (90,),
    },
}

if not os.environ.get('USE_OPENWISP_CELERY_TASK_ROUTES_DEFAULTS', True):
    task_routes = {}

app = Celery(
    'openwisp',
    include=['openwisp.tasks'],
    task_routes=task_routes,
    beat_schedule={
        **radius_schedule,
        **topology_schedule,
        **notification_schedule,
        **monitoring_schedule,
    },
)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
