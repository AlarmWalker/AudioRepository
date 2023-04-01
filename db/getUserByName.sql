DELIMITER //
DROP PROCEDURE IF EXISTS getUserByName //

CREATE PROCEDURE getUserByName(IN usernameIn VARCHAR(60))
BEGIN
  SELECT *
      FROM users
      WHERE username = usernameIn;
END //
DELIMITER ;
