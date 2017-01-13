import os
from unittest import skip

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase

from ..models import *


class ServerModelTestCase(TestCase):

    def setUp(self):
        pass

    def test_server_cpu(self):
        cpu_1 = ServerCPU.objects.create(
            physical_cores=2,
            smt=True,
            frequency=3200,
            make='make',
            model='cpu with smt')
        cpu_2 = ServerCPU.objects.create(
            physical_cores=2,
            smt=False,
            frequency=3200,
            make='make',
            model='cpu without smt')
        self.assertEqual(cpu_1.cores, 4)
        self.assertEqual(cpu_2.cores, 2)

    def test_server_drive(self):
        drive_1 = ServerDrive.objects.create(
            capacity=250,
            make='make',
            model='generic ssd',
            rpm=0)
        drive_2 = ServerDrive.objects.create(
            capacity=250,
            make='make',
            model='generic hdd',
            rpm=7200)
        self.assertEqual(drive_1.is_flash, True)
        self.assertEqual(drive_2.is_flash, False)