# Index column size too large. The maximum column size is 767 bytes.

Make sure the Database is created with `utf8mb4`. Also make sure these settings are set:

```sql
SET GLOBAL innodb_file_format = `Barracuda`;
SET GLOBAL innodb_file_per_table = `ON`;
SET GLOBAL innodb_large_prefix = `ON`;
```
