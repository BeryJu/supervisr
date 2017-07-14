"""
Supervisr Static Models
"""
from __future__ import unicode_literals

from datetime import timedelta

from django.db import models


class Basefiles(models.Model):
    """
    Bacula Imported Basefiles
    """
    BaseId = models.AutoField(db_column='BaseId', primary_key=True)
    BaseJobId = models.IntegerField(db_column='BaseJobId')
    JobId = models.IntegerField(db_column='JobId')
    FileId = models.BigIntegerField(db_column='FileId')
    FileIndex = models.IntegerField(db_column='FileIndex', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'BaseFiles'


class Cdimages(models.Model):
    """
    Bacula Imported Cdimages
    """
    MediaId = models.IntegerField(db_column='MediaId', primary_key=True)
    LastBurn = models.DateTimeField(db_column='LastBurn')

    class Meta:
        managed = False
        db_table = 'CDImages'


class Client(models.Model):
    """
    Bacula Imported Client
    """
    ClientId = models.AutoField(db_column='ClientId', primary_key=True)
    Name = models.TextField(db_column='Name', unique=True)
    Uname = models.TextField(db_column='Uname')
    AutoPrune = models.IntegerField(db_column='AutoPrune', blank=True, null=True)
    FileRetention = models.BigIntegerField(db_column='FileRetention', blank=True, null=True)
    JobRetention = models.BigIntegerField(db_column='JobRetention', blank=True, null=True)

    def __str__(self):
        return "Bacula Client %s" % self.Name

    class Meta:
        managed = False
        db_table = 'Client'
        sv_search_fields = ['Name', 'Uname']

class Counters(models.Model):
    """
    Bacula Imported Counters
    """
    Counter = models.TextField(db_column='Counter', primary_key=True)
    MinValue = models.IntegerField(db_column='MinValue', blank=True, null=True)
    MaxValue = models.IntegerField(db_column='MaxValue', blank=True, null=True)
    CurrentValue = models.IntegerField(db_column='CurrentValue', blank=True, null=True)
    WrapCounter = models.TextField(db_column='WrapCounter')

    class Meta:
        managed = False
        db_table = 'Counters'


class Device(models.Model):
    """
    Bacula Imported Device
    """
    DeviceId = models.AutoField(db_column='DeviceId', primary_key=True)
    Name = models.TextField(db_column='Name')
    MediaTypeId = models.IntegerField(db_column='MediaTypeId', blank=True, null=True)
    StorageId = models.IntegerField(db_column='StorageId', blank=True, null=True)
    DevMounts = models.IntegerField(db_column='DevMounts', blank=True, null=True)
    DevReadBytes = models.BigIntegerField(db_column='DevReadBytes', blank=True, null=True)
    DevWriteBytes = models.BigIntegerField(db_column='DevWriteBytes', blank=True, null=True)
    DevReadBytesSinceCleaning = models.BigIntegerField(db_column='DevReadBytesSinceCleaning',
                                                       blank=True, null=True)
    DevWriteBytesSinceCleaning = models.BigIntegerField(db_column='DevWriteBytesSinceCleaning',
                                                        blank=True, null=True)
    DevReadTime = models.BigIntegerField(db_column='DevReadTime', blank=True, null=True)
    DevWriteTime = models.BigIntegerField(db_column='DevWriteTime', blank=True, null=True)
    DevReadTimeSinceCleaning = models.BigIntegerField(db_column='DevReadTimeSinceCleaning',
                                                      blank=True, null=True)
    DevWriteTimeSinceCleaning = models.BigIntegerField(db_column='DevWriteTimeSinceCleaning',
                                                       blank=True, null=True)
    CleaningDate = models.DateTimeField(db_column='CleaningDate', blank=True, null=True)
    CleaningPeriod = models.BigIntegerField(db_column='CleaningPeriod', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Device'


class File(models.Model):
    """
    Bacula Imported File
    """
    FileId = models.BigAutoField(db_column='FileId', primary_key=True)
    FileIndex = models.IntegerField(db_column='FileIndex', blank=True, null=True)
    JobId = models.IntegerField(db_column='JobId')
    PathId = models.ForeignKey('Path', db_column='PathId')
    FilenameId = models.ForeignKey('Filename', db_column='FilenameId')
    DeltaSeq = models.SmallIntegerField(db_column='DeltaSeq', blank=True, null=True)
    MarkId = models.IntegerField(db_column='MarkId', blank=True, null=True)
    LStat = models.TextField(db_column='LStat')
    MD5 = models.TextField(db_column='MD5', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'File'


class Fileset(models.Model):
    """
    Bacula Imported Fileset
    """
    FileSetId = models.AutoField(db_column='FileSetId', primary_key=True)
    FileSet = models.TextField(db_column='FileSet')
    MD5 = models.TextField(db_column='MD5', blank=True, null=True)
    CreateTime = models.DateTimeField(db_column='CreateTime', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'FileSet'


class Filename(models.Model):
    """
    Bacula Imported Filename
    """
    FilenameId = models.AutoField(db_column='FilenameId', primary_key=True)
    Name = models.TextField(db_column='Name')

    class Meta:
        managed = False
        db_table = 'Filename'

class Job(models.Model):
    """
    Bacula Imported Job
    """
    JobId = models.AutoField(db_column='JobId', primary_key=True)
    Job = models.TextField(db_column='Job')
    Name = models.TextField(db_column='Name')
    Type = models.CharField(db_column='Type', max_length=1)
    Level = models.CharField(db_column='Level', max_length=1)
    ClientId = models.IntegerField(db_column='ClientId', blank=True, null=True)
    JobStatus = models.CharField(db_column='JobStatus', max_length=1)
    SchedTime = models.DateTimeField(db_column='SchedTime', blank=True, null=True)
    StartTime = models.DateTimeField(db_column='StartTime', blank=True, null=True)
    EndTime = models.DateTimeField(db_column='EndTime', blank=True, null=True)
    RealEndTime = models.DateTimeField(db_column='RealEndTime', blank=True, null=True)
    JobTDate = models.BigIntegerField(db_column='JobTDate', blank=True, null=True)
    VolSessionId = models.IntegerField(db_column='VolSessionId', blank=True, null=True)
    VolSessionTime = models.IntegerField(db_column='VolSessionTime', blank=True, null=True)
    JobFiles = models.IntegerField(db_column='JobFiles', blank=True, null=True)
    JobBytes = models.BigIntegerField(db_column='JobBytes', blank=True, null=True)
    ReadBytes = models.BigIntegerField(db_column='ReadBytes', blank=True, null=True)
    JobErrors = models.IntegerField(db_column='JobErrors', blank=True, null=True)
    JobMissingFiles = models.IntegerField(db_column='JobMissingFiles', blank=True, null=True)
    Pool = models.ForeignKey('Pool', db_column='PoolId', blank=True, null=True)
    FileSetId = models.IntegerField(db_column='FileSetId', blank=True, null=True)
    PriorJobId = models.IntegerField(db_column='PriorJobId', blank=True, null=True)
    PurgedFiles = models.IntegerField(db_column='PurgedFiles', blank=True, null=True)
    HasBase = models.IntegerField(db_column='HasBase', blank=True, null=True)
    HasCache = models.IntegerField(db_column='HasCache', blank=True, null=True)
    Reviewed = models.IntegerField(db_column='Reviewed', blank=True, null=True)
    Comment = models.TextField(db_column='Comment', blank=True, null=True)

    @property
    # pylint: disable=invalid-name
    def Icon(self):
        """
        Return Icon
        """
        return {
            'C': 'clock',
            'R': 'play',
            'B': 'clock',
            'T': 'success-standard',
            'E': 'warning-standard',
            'f': 'error-standard',
            'A': 'info-standard',
            'F': 'clock',
            'S': 'clock',
            'm': 'clock',
            'M': 'clock',
            's': 'clock',
            'j': 'clock',
            'c': 'clock',
            'd': 'clock',
            't': 'clock',
            'p': 'clock',
        }[self.JobStatus.decode("utf-8")]

    @property
    # pylint: disable=invalid-name
    def IconClass(self):
        """
        Return Icon Class
        """
        return {
            'C': 'is-highlight',
            'R': 'is-success',
            'B': 'is-highlight',
            'T': 'is-success',
            'E': 'is-warning',
            'f': 'is-error',
            'A': 'is-highlight',
            'F': 'is-highlight',
            'S': 'is-highlight',
            'm': 'is-highlight',
            'M': 'is-highlight',
            's': 'is-highlight',
            'j': 'is-highlight',
            'c': 'is-highlight',
            'd': 'is-highlight',
            't': 'is-highlight',
            'p': 'is-highlight',
        }[self.JobStatus.decode("utf-8")]

    @property
    # pylint: disable=invalid-name
    def ElapsedTime(self):
        """
        Calculate Duration
        """
        if not self.StartTime or not self.EndTime:
            return timedelta()
        return self.EndTime - self.StartTime

    @property
    # pylint: disable=invalid-name
    def Speed(self):
        """
        Calculate Speed
        """
        if self.ElapsedTime > timedelta():
            return self.ReadBytes / self.ElapsedTime.total_seconds()
        return 0

    def __str__(self):
        return "Bacula Job %s" % self.Job

    class Meta:
        managed = False
        db_table = 'Job'
        sv_search_fields = ['Job',]


class Jobhisto(models.Model):
    """
    Bacula Imported Jobhisto
    """
    JobId = models.IntegerField(db_column='JobId')
    Job = models.TextField(db_column='Job')
    Name = models.TextField(db_column='Name')
    Type = models.CharField(db_column='Type', max_length=1)
    Level = models.CharField(db_column='Level', max_length=1)
    ClientId = models.IntegerField(db_column='ClientId', blank=True, null=True)
    JobStatus = models.CharField(db_column='JobStatus', max_length=1)
    SchedTime = models.DateTimeField(db_column='SchedTime', blank=True, null=True)
    StartTime = models.DateTimeField(db_column='StartTime', blank=True, null=True)
    EndTime = models.DateTimeField(db_column='EndTime', blank=True, null=True)
    RealEndTime = models.DateTimeField(db_column='RealEndTime', blank=True, null=True)
    JobTDate = models.BigIntegerField(db_column='JobTDate', blank=True, null=True)
    VolSessionId = models.IntegerField(db_column='VolSessionId', blank=True, null=True)
    VolSessionTime = models.IntegerField(db_column='VolSessionTime', blank=True, null=True)
    JobFiles = models.IntegerField(db_column='JobFiles', blank=True, null=True)
    JobBytes = models.BigIntegerField(db_column='JobBytes', blank=True, null=True)
    ReadBytes = models.BigIntegerField(db_column='ReadBytes', blank=True, null=True)
    JobErrors = models.IntegerField(db_column='JobErrors', blank=True, null=True)
    JobMissingFiles = models.IntegerField(db_column='JobMissingFiles', blank=True, null=True)
    PoolId = models.IntegerField(db_column='PoolId', blank=True, null=True)
    FileSetId = models.IntegerField(db_column='FileSetId', blank=True, null=True)
    PriorJobId = models.IntegerField(db_column='PriorJobId', blank=True, null=True)
    PurgedFiles = models.IntegerField(db_column='PurgedFiles', blank=True, null=True)
    HasBase = models.IntegerField(db_column='HasBase', blank=True, null=True)
    HasCache = models.IntegerField(db_column='HasCache', blank=True, null=True)
    Reviewed = models.IntegerField(db_column='Reviewed', blank=True, null=True)
    Comment = models.TextField(db_column='Comment', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'JobHisto'


class JobMedia(models.Model):
    """
    Bacula Imported JobMedia
    """
    JobMediaId = models.AutoField(db_column='JobMediaId', primary_key=True)
    JobId = models.IntegerField(db_column='JobId')
    MediaId = models.IntegerField(db_column='MediaId')
    FirstIndex = models.IntegerField(db_column='FirstIndex', blank=True, null=True)
    LastIndex = models.IntegerField(db_column='LastIndex', blank=True, null=True)
    StartFile = models.IntegerField(db_column='StartFile', blank=True, null=True)
    EndFile = models.IntegerField(db_column='EndFile', blank=True, null=True)
    StartBlock = models.IntegerField(db_column='StartBlock', blank=True, null=True)
    EndBlock = models.IntegerField(db_column='EndBlock', blank=True, null=True)
    VolIndex = models.IntegerField(db_column='VolIndex', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'JobMedia'


class Location(models.Model):
    """
    Bacula Imported Location
    """
    LocationId = models.AutoField(db_column='LocationId', primary_key=True)
    Location = models.TextField(db_column='Location')
    Cost = models.IntegerField(db_column='Cost', blank=True, null=True)
    Enabled = models.IntegerField(db_column='Enabled', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Location'


class Locationlog(models.Model):
    """
    Bacula Imported Locationlog
    """
    LocLogId = models.AutoField(db_column='LocLogId', primary_key=True)
    Date = models.DateTimeField(db_column='Date', blank=True, null=True)
    Comment = models.TextField(db_column='Comment')
    MediaId = models.IntegerField(db_column='MediaId', blank=True, null=True)
    LocationId = models.IntegerField(db_column='LocationId', blank=True, null=True)
    NewVolStatus = models.CharField(db_column='NewVolStatus', max_length=9)
    NewEnabled = models.IntegerField(db_column='NewEnabled', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'LocationLog'


class Log(models.Model):
    """
    Bacula Imported Log
    """
    LogId = models.AutoField(db_column='LogId', primary_key=True)
    JobId = models.IntegerField(db_column='JobId', blank=True, null=True)
    Time = models.DateTimeField(db_column='Time', blank=True, null=True)
    LogText = models.TextField(db_column='LogText')

    def __str__(self):
        return "Bacula Log %s" % self.LogText

    class Meta:
        managed = False
        db_table = 'Log'

class Media(models.Model):
    """
    Bacula Imported Media
    """
    MediaId = models.AutoField(db_column='MediaId', primary_key=True)
    VolumeName = models.TextField(db_column='VolumeName', unique=True)
    Slot = models.IntegerField(db_column='Slot', blank=True, null=True)
    PoolId = models.IntegerField(db_column='PoolId', blank=True, null=True)
    MediaType = models.TextField(db_column='MediaType')
    MediaTypeId = models.IntegerField(db_column='MediaTypeId', blank=True, null=True)
    LabelType = models.IntegerField(db_column='LabelType', blank=True, null=True)
    FirstWritten = models.DateTimeField(db_column='FirstWritten', blank=True, null=True)
    LastWritten = models.DateTimeField(db_column='LastWritten', blank=True, null=True)
    LabelDate = models.DateTimeField(db_column='LabelDate', blank=True, null=True)
    VolJobs = models.IntegerField(db_column='VolJobs', blank=True, null=True)
    VolFiles = models.IntegerField(db_column='VolFiles', blank=True, null=True)
    VolBlocks = models.IntegerField(db_column='VolBlocks', blank=True, null=True)
    VolMounts = models.IntegerField(db_column='VolMounts', blank=True, null=True)
    VolBytes = models.BigIntegerField(db_column='VolBytes', blank=True, null=True)
    VolParts = models.IntegerField(db_column='VolParts', blank=True, null=True)
    VolErrors = models.IntegerField(db_column='VolErrors', blank=True, null=True)
    VolWrites = models.BigIntegerField(db_column='VolWrites', blank=True, null=True)
    VolCapacityBytes = models.BigIntegerField(db_column='VolCapacityBytes', blank=True, null=True)
    VolStatus = models.CharField(db_column='VolStatus', max_length=9)
    Enabled = models.IntegerField(db_column='Enabled', blank=True, null=True)
    Recycle = models.IntegerField(db_column='Recycle', blank=True, null=True)
    ActionOnPurge = models.IntegerField(db_column='ActionOnPurge', blank=True, null=True)
    VolRetention = models.BigIntegerField(db_column='VolRetention', blank=True, null=True)
    VolUseDuration = models.BigIntegerField(db_column='VolUseDuration', blank=True, null=True)
    MaxVolJobs = models.IntegerField(db_column='MaxVolJobs', blank=True, null=True)
    MaxVolFiles = models.IntegerField(db_column='MaxVolFiles', blank=True, null=True)
    MaxVolBytes = models.BigIntegerField(db_column='MaxVolBytes', blank=True, null=True)
    InChanger = models.IntegerField(db_column='InChanger', blank=True, null=True)
    StorageId = models.IntegerField(db_column='StorageId', blank=True, null=True)
    DeviceId = models.IntegerField(db_column='DeviceId', blank=True, null=True)
    MediaAddressing = models.IntegerField(db_column='MediaAddressing', blank=True, null=True)
    VolReadTime = models.BigIntegerField(db_column='VolReadTime', blank=True, null=True)
    VolWriteTime = models.BigIntegerField(db_column='VolWriteTime', blank=True, null=True)
    EndFile = models.IntegerField(db_column='EndFile', blank=True, null=True)
    EndBlock = models.IntegerField(db_column='EndBlock', blank=True, null=True)
    LocationId = models.IntegerField(db_column='LocationId', blank=True, null=True)
    RecycleCount = models.IntegerField(db_column='RecycleCount', blank=True, null=True)
    InitialWrite = models.DateTimeField(db_column='InitialWrite', blank=True, null=True)
    ScratchPoolId = models.IntegerField(db_column='ScratchPoolId', blank=True, null=True)
    RecyclePoolId = models.IntegerField(db_column='RecyclePoolId', blank=True, null=True)
    Comment = models.TextField(db_column='Comment', blank=True, null=True)
    VolABytes = models.BigIntegerField(db_column='VolABytes', blank=True, null=True)
    VolAPadding = models.BigIntegerField(db_column='VolAPadding', blank=True, null=True)
    VolHoleBytes = models.BigIntegerField(db_column='VolHoleBytes', blank=True, null=True)
    VolHoles = models.IntegerField(db_column='VolHoles', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Media'


class Mediatype(models.Model):
    """
    Bacula Imported Mediatype
    """
    MediaTypeId = models.AutoField(db_column='MediaTypeId', primary_key=True)
    MediaType = models.TextField(db_column='MediaType')
    ReadOnly = models.IntegerField(db_column='ReadOnly', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'MediaType'


class Path(models.Model):
    """
    Bacula Imported Path
    """
    PathId = models.AutoField(db_column='PathId', primary_key=True)
    Path = models.TextField(db_column='Path')

    class Meta:
        managed = False
        db_table = 'Path'


class Pathhierarchy(models.Model):
    """
    Bacula Imported Pathhierarchy
    """
    PathId = models.IntegerField(db_column='PathId', primary_key=True)
    PPathId = models.IntegerField(db_column='PPathId')

    class Meta:
        managed = False
        db_table = 'PathHierarchy'


class Pathvisibility(models.Model):
    """
    Bacula Imported Pathvisibility
    """
    PathId = models.IntegerField(db_column='PathId')
    JobId = models.IntegerField(db_column='JobId', primary_key=True)
    Size = models.BigIntegerField(db_column='Size', blank=True, null=True)
    Files = models.IntegerField(db_column='Files', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PathVisibility'
        unique_together = (('JobId', 'PathId'),)


class Pool(models.Model):
    """
    Bacula Imported Pool
    """
    PoolId = models.AutoField(db_column='PoolId', primary_key=True)
    Name = models.TextField(db_column='Name', unique=True)
    NumVols = models.IntegerField(db_column='NumVols', blank=True, null=True)
    MaxVols = models.IntegerField(db_column='MaxVols', blank=True, null=True)
    UseOnce = models.IntegerField(db_column='UseOnce', blank=True, null=True)
    UseCatalog = models.IntegerField(db_column='UseCatalog', blank=True, null=True)
    AcceptAnyVolume = models.IntegerField(db_column='AcceptAnyVolume', blank=True, null=True)
    VolRetention = models.BigIntegerField(db_column='VolRetention', blank=True, null=True)
    VolUseDuration = models.BigIntegerField(db_column='VolUseDuration', blank=True, null=True)
    MaxVolJobs = models.IntegerField(db_column='MaxVolJobs', blank=True, null=True)
    MaxVolFiles = models.IntegerField(db_column='MaxVolFiles', blank=True, null=True)
    MaxVolBytes = models.BigIntegerField(db_column='MaxVolBytes', blank=True, null=True)
    AutoPrune = models.IntegerField(db_column='AutoPrune', blank=True, null=True)
    Recycle = models.IntegerField(db_column='Recycle', blank=True, null=True)
    ActionOnPurge = models.IntegerField(db_column='ActionOnPurge', blank=True, null=True)
    PoolType = models.CharField(db_column='PoolType', max_length=9)
    LabelType = models.IntegerField(db_column='LabelType', blank=True, null=True)
    LabelFormat = models.TextField(db_column='LabelFormat', blank=True, null=True)
    Enabled = models.IntegerField(db_column='Enabled', blank=True, null=True)
    ScratchPoolId = models.IntegerField(db_column='ScratchPoolId', blank=True, null=True)
    RecyclePoolId = models.IntegerField(db_column='RecyclePoolId', blank=True, null=True)
    NextPoolId = models.IntegerField(db_column='NextPoolId', blank=True, null=True)
    MigrationHighBytes = models.BigIntegerField(db_column='MigrationHighBytes', blank=True,
                                                null=True)
    MigrationLowBytes = models.BigIntegerField(db_column='MigrationLowBytes', blank=True, null=True)
    MigrationTime = models.BigIntegerField(db_column='MigrationTime', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Pool'


class Restoreobject(models.Model):
    """
    Bacula Imported Restoreobject
    """
    RestoreObjectId = models.AutoField(db_column='RestoreObjectId', primary_key=True)
    ObjectName = models.TextField(db_column='ObjectName')
    RestoreObject = models.TextField(db_column='RestoreObject')
    PluginName = models.TextField(db_column='PluginName')
    ObjectLength = models.IntegerField(db_column='ObjectLength', blank=True, null=True)
    ObjectFullLength = models.IntegerField(db_column='ObjectFullLength', blank=True, null=True)
    ObjectIndex = models.IntegerField(db_column='ObjectIndex', blank=True, null=True)
    ObjectType = models.IntegerField(db_column='ObjectType', blank=True, null=True)
    FileIndex = models.IntegerField(db_column='FileIndex', blank=True, null=True)
    JobId = models.IntegerField(db_column='JobId')
    ObjectCompression = models.IntegerField(db_column='ObjectCompression', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'RestoreObject'


class Snapshot(models.Model):
    """
    Bacula Imported Snapshot
    """
    SnapshotId = models.AutoField(db_column='SnapshotId', primary_key=True)
    Name = models.TextField(db_column='Name')
    JobId = models.IntegerField(db_column='JobId', blank=True, null=True)
    FileSetId = models.IntegerField(db_column='FileSetId', blank=True, null=True)
    CreateTDate = models.BigIntegerField(db_column='CreateTDate')
    CreateDate = models.DateTimeField(db_column='CreateDate')
    ClientId = models.IntegerField(db_column='ClientId', blank=True, null=True)
    Volume = models.TextField(db_column='Volume')
    Device = models.TextField(db_column='Device')
    Type = models.TextField(db_column='Type')
    Retention = models.IntegerField(db_column='Retention', blank=True, null=True)
    Comment = models.TextField(db_column='Comment', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Snapshot'
        unique_together = (('Device', 'Volume', 'Name'),)


class Status(models.Model):
    """
    Bacula Imported Status
    """
    JobStatus = models.CharField(db_column='JobStatus', primary_key=True, max_length=1)
    JobStatusLong = models.TextField(db_column='JobStatusLong', blank=True, null=True)
    Severity = models.IntegerField(db_column='Severity', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Status'


class Storage(models.Model):
    """
    Bacula Imported Storage
    """
    StorageId = models.AutoField(db_column='StorageId', primary_key=True)
    Name = models.TextField(db_column='Name')
    AutoChanger = models.IntegerField(db_column='AutoChanger', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Storage'


class Unsavedfiles(models.Model):
    """
    Bacula Imported Unsavedfiles
    """
    UnsavedId = models.AutoField(db_column='UnsavedId', primary_key=True)
    JobId = models.IntegerField(db_column='JobId')
    PathId = models.IntegerField(db_column='PathId')
    FilenameId = models.IntegerField(db_column='FilenameId')

    class Meta:
        managed = False
        db_table = 'UnsavedFiles'


class Version(models.Model):
    """
    Bacula Imported Version
    """
    VersionId = models.IntegerField(db_column='VersionId')

    class Meta:
        managed = False
        db_table = 'Version'
