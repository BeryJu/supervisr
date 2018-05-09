"""Supervisr DNS Util Test"""
from django.test import TestCase

# from supervisr.dns.utils import zone_to_rec

BIND_ZONE = """
$ORIGIN .
$TTL 600        ; 10 minutes
beryju.org        IN    SOA    ns1.s.beryju.org.    support.beryju.org. (
                    2017102802    ; serial
                    1800        ; refresh (30 minutes)
                    180        ; retry (3 minutes)
                    2419200        ; expire (4 weeks)
                    86400        ; minimum (1 day)
                    )

$ORIGIN beryju.org.
@            NS      ns1.s.beryju.org.
@            NS      ns2.s.beryju.org.
@            NS      ns3.s.beryju.org.
@            A       163.172.31.151
@            A       163.172.31.152
             A       1.2.3.4
@            AAAA    2001:1620:20d1:100::2
@            MX      10    mx1.s.beryju.org.
@            MX      20    mx2.s.beryju.org.

@            TXT     "v=spf1 include:_spf.beryju.org ~all"
www         A        163.172.31.151
            A        163.172.31.152
            AAAA     2001:1620:20d1:100::2
"""


class TestUtils(TestCase):
    """Supervisr DNS Util Test"""

    # def test_util_zone_to_rec(self):
    #     """Test bind zone importer"""
    #     zone_to_rec(BIND_ZONE)
