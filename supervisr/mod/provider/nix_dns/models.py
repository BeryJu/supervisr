"""supervisr powerdns models"""

from django.db import models


class Comment(models.Model):
    """PowerDNS imported Comment"""

    domain = models.ForeignKey('Domain', models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    modified_at = models.IntegerField()
    account = models.CharField(max_length=40)
    comment = models.TextField()

    class Meta:
        db_table = 'comments'


class Cryptokey(models.Model):
    """PowerDNS imported Cryptokey"""

    domain = models.ForeignKey('Domain', models.CASCADE)
    flags = models.IntegerField()
    active = models.IntegerField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'cryptokeys'


class DomainMetadata(models.Model):
    """PowerDNS imported DomainMetadata"""

    domain = models.ForeignKey('Domain', models.CASCADE)
    kind = models.CharField(max_length=32, blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'domainmetadata'


class Domain(models.Model):
    """PowerDNS imported Domain"""

    name = models.CharField(unique=True, max_length=255)
    master = models.CharField(max_length=128, blank=True, null=True)
    last_check = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField(blank=True, null=True)
    account = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        db_table = 'domains'


class Record(models.Model):
    """PowerDNS imported Record"""

    id = models.BigAutoField(primary_key=True)
    domain = models.ForeignKey('Domain', models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    ttl = models.IntegerField(blank=True, null=True)
    prio = models.IntegerField(blank=True, null=True)
    change_date = models.IntegerField(blank=True, null=True) # TODO: Automatically set this on save
    disabled = models.IntegerField(blank=True, null=True)
    ordername = models.CharField(max_length=255, blank=True, null=True)
    auth = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'records'


class Supermaster(models.Model):
    """PowerDNS imported Supermaster"""

    ip = models.CharField(primary_key=True, max_length=64)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40)

    class Meta:
        db_table = 'supermasters'
        unique_together = (('ip', 'nameserver'),)


class TSIGKey(models.Model):
    """PowerDNS imported TSIGKey"""

    name = models.CharField(max_length=255, blank=True, null=True)
    algorithm = models.CharField(max_length=50, blank=True, null=True)
    secret = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tsigkeys'
        unique_together = (('name', 'algorithm'),)
