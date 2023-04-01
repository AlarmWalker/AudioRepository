DELIMITER //
DROP PROCEDURE IF EXISTS addUser //
CREATE PROCEDURE addUser
(
   IN usernameIn varchar(60)
)
BEGIN
    INSERT INTO users(username) VALUES (usernameIn);
    IF(ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52711'
        SET MESSAGE_TEXT = 'Unable to create user.';
    END IF;

    SELECT LAST_INSERT_ID();

END //
DELIMITER ;
