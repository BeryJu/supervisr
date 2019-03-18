"""Supervisr nix_dns Settings"""

DATABASE_ROUTERS = [
    'supervisr.provider.nix_dns.router.PowerDNSRouter',
]
