DELIMITER //
DROP PROCEDURE IF EXISTS deleteUserAudio //
CREATE PROCEDURE deleteUserAudio
(
    IN audioIDIn INT,
    IN ownerIDIn INT
)
BEGIN
    DECLARE v_ownerID INT;

    SELECT userID
    INTO v_ownerID
    FROM audios
    WHERE audioID = audioIDIn;
    
    IF(v_ownerID = ownerIDIn) THEN
        DELETE FROM audios
        WHERE audioID = audioIDIn;
        
        IF(ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to delete the audio.';
        END IF;
    ELSE
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Access Denied.';
    END IF;

END //
DELIMITER ;
