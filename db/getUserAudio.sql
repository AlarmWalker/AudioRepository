DELIMITER //
DROP PROCEDURE IF EXISTS getUserAudio //
CREATE PROCEDURE getUserAudio
(
    IN userIdIn INT, 
    In audioIdIn INT
)
BEGIN
    SELECT *
      FROM audios
        WHERE audioID = audioIdIn AND userId = userIdIn;

END //
DELIMITER ;
