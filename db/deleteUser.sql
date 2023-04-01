DELIMITER //
DROP PROCEDURE IF EXISTS deleteUser //
CREATE PROCEDURE deleteUser
(
   IN userIdIn INT
)
BEGIN
    DELETE
        FROM audios WHERE userId = userIDIn;
    DELETE
	FROM users WHERE userId = userIdIn;
    IF(ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52711'
        SET MESSAGE_TEXT = 'Unable to delete user.';
    END IF;

    SELECT LAST_INSERT_ID();

END //
DELIMITER ;
