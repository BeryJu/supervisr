"""
Supervisr DNS Utils
"""

import dns.name
import dns.query
import dns.rdata
import dns.rdataclass
import dns.rdatatype
import dns.tokenizer
import dns.zone
from dns.rdtypes.ANY.MX import MX
from dns.rdtypes.ANY.SOA import SOA

from supervisr.dns.models import Record


def zone_to_rec(data, root_zone=''):
    """
    Convert BIND zone to DB records
    """
    records = []
    # dnspython doesn't like line returns
    data = data.replace('\r', '')
    zone = dns.zone.from_text(data, check_origin=False, relativize=False)
    _soa = None
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
                content = str(dset_data)
                # MX records need to have their exchange extracted seperately
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
                # SOA record should last in list, so auto-serial update
                # isn't triggered
                if isinstance(dset_data, SOA):
                    _soa = _rec
                else:
                    records.append(_rec)
    records.append(_soa)
    return records

def rec_to_rd(rec: Record) -> dns.rdata.Rdata:
    """Convert record to RDATA"""
    rtype = dns.rdatatype.from_text(rec.type)
    cls = dns.rdataclass.IN
    origin = dns.name.from_text(rec.domain.domain.domain)
    tok = dns.tokenizer.Tokenizer(rec.content, '<string>')
    return dns.rdata.from_text(cls, rtype, tok, origin, False)
