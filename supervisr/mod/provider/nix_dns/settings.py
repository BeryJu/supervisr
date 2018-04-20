"""Supervisr nix_dns Settings"""

DATABASE_ROUTERS = [
    'supervisr.mod.provider.nix_dns.router.PowerDNSRouter',
]
