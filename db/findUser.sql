DELIMITER //
DROP PROCEDURE IF EXISTS findUser //
CREATE PROCEDURE findUser(IN usernameIn VARCHAR(60))
BEGIN
  SELECT userId 
      FROM users
      WHERE username = usernameIn;
END //
DELIMITER ;
