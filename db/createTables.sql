DROP TABLE IF EXISTS users;
CREATE TABLE users (
  userID    INT             NOT NULL AUTO_INCREMENT,
  userName  varchar(45)     NOT NULL,
  PRIMARY KEY (userID)
);

DROP TABLE IF EXISTS audios;
CREATE TABLE audios (
  audioID       INT             NOT NULL AUTO_INCREMENT,
  userID        INT             NOT NULL,
  audioName     varchar(45)     NOT NULL,
  audioFile     varchar(100)    NOT NULL,
  PRIMARY KEY (audioID),
  FOREIGN KEY (userID) REFERENCES users (userID)
); 
