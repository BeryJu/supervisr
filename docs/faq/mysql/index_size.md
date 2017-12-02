# Index column size too large. The maximum column size is 767 bytes.

Make sure the Database is created with `utf8mb4`. Also make sure these settings are set:

```sql
ALTER DATABASE supervisr CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
SET GLOBAL innodb_file_format = `Barracuda`;
SET GLOBAL innodb_file_per_table = `ON`;
SET GLOBAL innodb_large_prefix = `ON`;
```
