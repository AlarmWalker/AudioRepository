DELIMITER //
DROP PROCEDURE IF EXISTS getAllAudio //
CREATE PROCEDURE getAllAudio()
BEGIN
    SELECT * FROM audios;

END //
DELIMITER ;
