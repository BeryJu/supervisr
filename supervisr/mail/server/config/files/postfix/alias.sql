DELIMITER //
CREATE PROCEDURE `alias`
(orig_mail TEXT, domain TEXT)
BEGIN
SET @input = orig_mail;
  SET @plus_idx =
    (SELECT INSTR(@input, '+'));
  SET @cut_length =
    (SELECT
       (SELECT INSTR(@input, '@')) - @plus_idx);
  SET @has_plus =
    (SELECT @plus_idx > 0);
  SET @extension =
    (SELECT SUBSTRING(@input, @plus_idx, @cut_length));
  SET @without =
    (SELECT REPLACE(@input, @extension, ''));
  SET @real_email = IF(@has_plus, @without, @input);
  SET @found_email =
    (SELECT `supervisr_mail_mailalias`.`destination`
      FROM `supervisr_mail_mailalias`
      WHERE `supervisr_mail_mailalias`.`account_id` =
          (SELECT `supervisr_mail_mailaccount`.`product_ptr_id`
           FROM `supervisr_mail_mailaccount`
           WHERE `supervisr_mail_mailaccount`.`email_raw` = @real_email
             AND `supervisr_mail_mailaccount`.`is_catchall` = 0)
        UNION ALL
        SELECT `supervisr_mail_mailaccount`.`email_raw`
        FROM `supervisr_mail_mailaccount` WHERE `supervisr_mail_mailaccount`.`email_raw` = @real_email
      LIMIT 1);
  SET @found_email_repl = (
    SELECT REPLACE(@found_email, '@', (SELECT CONCAT(@extension, '@'))) AS email);
  SELECT * FROM (SELECT @found_email_repl AS email
      UNION ALL
      SELECT `supervisr_mail_mailalias`.`destination` AS email
      FROM `supervisr_mail_mailalias` WHERE `supervisr_mail_mailalias`.`account_id` =
        (SELECT `supervisr_mail_mailaccount`.`product_ptr_id`
         FROM `supervisr_mail_mailaccount`
         WHERE `supervisr_mail_mailaccount`.`domain_raw` = domain
           AND `supervisr_mail_mailaccount`.`is_catchall` = 1)) AS final_email
  WHERE email IS NOT NULL
  LIMIT 1;
END //
DELIMITER ;
