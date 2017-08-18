"""
Supervisr DNS Utils
"""

import dns.query
import dns.rdataclass
import dns.rdatatype
import dns.zone
from dns.rdtypes.ANY.MX import MX

from supervisr.dns.models import Record


def zone_to_rec(data, root_zone=''):
    """
    Convert BIND zone to DB records
    """
    records = []
    # dnspython doesn't like line returns
    data = data.replace('\r', '')
    zone = dns.zone.from_text(data, check_origin=False, relativize=False)

    names = zone.nodes.keys()
    for name in names:
        for dset in zone[name].rdatasets:
            for dset_data in dset:
                r_name = str(name).replace(root_zone, '')
                # Remove trailing dot since powerdns trims this too
                if '.' in r_name and r_name[-1] == '.':
                    r_name = r_name[:-1]
                # Root records are renamed to be @
                if r_name == '':
                    r_name = '@'
                # MX records need to have their exchange extracted seperately
                content = str(dset_data)
                if isinstance(dset_data, MX):
                    content = dset_data.exchange
                _rec = Record(
                    name=r_name,
                    type=dns.rdatatype.to_text(dset.rdtype),
                    content=content,
                    ttl=dset.ttl)
                # TODO: Remove Priority from content if set
                if getattr(dset_data, 'preference', None):
                    _rec.prio = dset_data.preference
                records.append(_rec)
    return records
