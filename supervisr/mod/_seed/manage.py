#!/usr/bin/env python3
"""
Django Launcher
"""
import os
import sys

import pymysql

pymysql.install_as_MySQLdb()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supervisr.core.settings")
    os.environ.setdefault("SUPERVISR_LOCAL_SETTINGS", "local_settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
