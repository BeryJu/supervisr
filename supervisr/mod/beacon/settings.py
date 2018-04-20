"""supervisr mod beacon settings"""

from datetime import timedelta

CELERY_BEAT_SCHEDULE = {
    'send-beacons': {
        'task': 'supervisr.mod.beacon.tasks.run_sender',
        'schedule': timedelta(minutes=15),
        'options': {'queue': 'supervisr.mod.beacon'}
    }
}
