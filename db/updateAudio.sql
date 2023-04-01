DELIMITER //
DROP PROCEDURE IF EXISTS updateAudio //
CREATE PROCEDURE updateAudio
(
    IN audioIDIn INT,
    IN audioNameIn VARCHAR(45)
)
BEGIN
    UPDATE audios
    SET audioName = audioNameIn
    WHERE audioID = audioIDIn;

END //
DELIMITER ;

