DELIMITER //
DROP PROCEDURE IF EXISTS getAudioById //
CREATE PROCEDURE getAudioById(IN audioIdIn INT)
BEGIN
    SELECT *
      FROM audios
        WHERE audioID = audioIdIn;

END //
DELIMITER ;
