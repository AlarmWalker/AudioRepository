DELIMITER //
DROP PROCEDURE IF EXISTS getUserAudioLibrary //
CREATE PROCEDURE getUserAudioLibrary(IN userIDIn INT)
BEGIN
    SELECT *
    FROM audios
    WHERE userID = userIDIn;
END //
DELIMITER ;
