"""supervisr Stats Influx Settings to load middleware"""

CELERY_BEAT_SCHEDULE = {
    'send-influx-stats': {
        'task': 'supervisr.mod.stats.influx.tasks.push_influx_data',
        'schedule': 10,
        'options': {'queue': 'supervisr.mod.stats.influx'}
    }
}
