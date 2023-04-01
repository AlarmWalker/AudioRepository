DELIMITER //
DROP PROCEDURE IF EXISTS addAudio //
CREATE PROCEDURE addAudio
(
   IN audioNameIn VARCHAR(45),
   IN audioFileIn VARCHAR(255),
   IN userIdIn INT
)
BEGIN
    INSERT INTO audios (userId, audioName, audioFile) VALUES (userIdIn, audioNameIn, audioFileIn);

    IF (ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52711'
        SET MESSAGE_TEXT = 'Unable to create the audio.';
    END IF;

    
    SELECT LAST_INSERT_ID(); 

END //
DELIMITER ;
