DELIMITER //
DROP PROCEDURE IF EXISTS updateUserAudio //
CREATE PROCEDURE updateUserAudio
(
    IN audioIDIn INT,
    IN audioNameIn VARCHAR(45),
    IN executingUserID INT
)
BEGIN

    DECLARE v_ownerID INT;
    
    SELECT userID
    INTO v_ownerID
    FROM audios
    WHERE audioID = audioIDIn;
    
    IF (v_ownerID = executingUserID) THEN
        UPDATE audios
        SET audioName = audioNameIn
        WHERE audioID = audioIDIn;
        
        IF(ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to update the audio.';
        END IF;
    ELSE
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Access Denied.';
    END IF;

END //
DELIMITER ;
