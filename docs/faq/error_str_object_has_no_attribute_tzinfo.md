# error'str' object has no attribute 'tzinfo'

This error can happen in supervisr.mod.contrib.bacula, when bacula is using an older MySQL version.
Older MySQL versions (<=5.6) don't require default timestampts to be valid, so they get set to `0000-00-00 00:00:00`, which is invalid.
Use this command on your bacula database to fix the error:

```mysql
-- Table Job
ALTER TABLE Job MODIFY COLUMN SchedTime datetime DEFAULT '1970-01-01 00:00:00';
ALTER TABLE Job MODIFY COLUMN StartTime datetime DEFAULT '1970-01-01 00:00:00';
ALTER TABLE Job MODIFY COLUMN EndTime datetime DEFAULT '1970-01-01 00:00:00';
ALTER TABLE Job MODIFY COLUMN RealEndTime datetime DEFAULT '1970-01-01 00:00:00';
UPDATE Job SET SchedTime = '1970-01-01 00:00:00' WHERE SchedTime = '0000-00-00 00:00:00';
UPDATE Job SET StartTime = '1970-01-01 00:00:00' WHERE StartTime = '0000-00-00 00:00:00';
UPDATE Job SET EndTime = '1970-01-01 00:00:00' WHERE EndTime = '0000-00-00 00:00:00';
UPDATE Job SET RealEndTime = '1970-01-01 00:00:00' WHERE RealEndTime = '0000-00-00 00:00:00';
-- Table Media
ALTER TABLE Media MODIFY COLUMN FirstWritten datetime DEFAULT '1970-01-01 00:00:00';
ALTER TABLE Media MODIFY COLUMN LastWritten datetime DEFAULT '1970-01-01 00:00:00';
ALTER TABLE Media MODIFY COLUMN LabelDate datetime DEFAULT '1970-01-01 00:00:00';
ALTER TABLE Media MODIFY COLUMN InitialWrite datetime DEFAULT '1970-01-01 00:00:00';
UPDATE Media SET FirstWritten = '1970-01-01 00:00:00' WHERE FirstWritten = '0000-00-00 00:00:00';
UPDATE Media SET LastWritten = '1970-01-01 00:00:00' WHERE LastWritten = '0000-00-00 00:00:00';
UPDATE Media SET LabelDate = '1970-01-01 00:00:00' WHERE LabelDate = '0000-00-00 00:00:00';
UPDATE Media SET InitialWrite = '1970-01-01 00:00:00' WHERE InitialWrite = '0000-00-00 00:00:00';
```
