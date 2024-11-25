from __future__ import absolute_import, unicode_literals

import os

from celery import shared_task
from django.core import management


@shared_task
def radius_tasks():
    management.call_command(
        "delete_old_radacct", int(os.environ['CRON_DELETE_OLD_RADACCT'])
    )
    management.call_command(
        "delete_old_postauth", int(os.environ['CRON_DELETE_OLD_POSTAUTH'])
    )
    management.call_command(
        "cleanup_stale_radacct", int(os.environ['CRON_CLEANUP_STALE_RADACCT'])
    )
    management.call_command("deactivate_expired_users")
    management.call_command(
        "delete_old_radiusbatch_users",
        older_than_days=int(os.environ['CRON_DELETE_OLD_RADIUSBATCH_USERS']),
    )


@shared_task
def save_snapshot():
    management.call_command("save_snapshot")


@shared_task
def update_topology():
    management.call_command("update_topology")
