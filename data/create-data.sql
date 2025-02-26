CREATE TABLE MotionPicture(
    id INT NOT NULL PRIMARY KEY,
    NAME VARCHAR(100),
    rating INT CHECK (rating>=0 AND rating<=10),
    production VARCHAR(100),
    budget INT CHECK (budget>0)
)

CREATE TABLE User(
    email VARCHAR(100) NOT NULL PRIMARY KEY,
    NAME VARCHAR(100),
    age INT
)

CREATE TABLE Likes(
    uemail VARCHAR(100) NOT NULL,
    mpid INT NOT NULL,
    PRIMARY KEY (uemail, mpid),
    FOREIGN KEY (uemail) REFERENCES User(email)
        ON DELETE CASCADE,
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
        ON DELETE CASCADE
)

CREATE TABLE Movie(
    mpid INT NOT NULL PRIMARY KEY,
    boxoffice_collection FLOAT CHECK (boxoffice_collection>=0),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
        ON DELETE CASCADE
)

CREATE TABLE Series(
    mpid INT NOT NULL PRIMARY KEY,
    season_count INT CHECK (season_count>=1),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
        ON DELETE CASCADE
)