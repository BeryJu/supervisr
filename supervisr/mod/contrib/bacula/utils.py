"""
Supervisr Bacula Utilrs
"""
from math import log

from django.conf import settings
from django.db import connections

UNIT_LIST = list(zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2]))
def size_human(num):
    """Human friendly file size"""
    if not num:
        return 0
    if num > 1:
        exponent = min(int(log(num, 1024)), len(UNIT_LIST) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = UNIT_LIST[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'


def db_size(db_alias='bacula'):
    """
    Get database size in bytes
    """
    cursor = connections[db_alias].cursor()
    db_name = settings.DATABASES[db_alias]['NAME']
    cursor.execute("""
        SELECT table_schema                                        "%s",
           Sum(data_length + index_length) "size"
        FROM   information_schema.tables
        GROUP  BY table_schema;
    """ % db_name)
    row = cursor.fetchone()
    return int(row[1])
