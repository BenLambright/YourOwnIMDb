CREATE TABLE MotionPicture(
    id INT NOT NULL PRIMARY KEY,
    name VARCHAR(100), 
    rating INT,
    production VARCHAR(100), 
    budget INT
);

CREATE TABLE User(
    email VARCHAR(100) NOT NULL PRIMARY KEY,
    name VARCHAR(100), 
    age INT
);

CREATE TABLE Likes(
    uemail VARCHAR(100) NOT NULL,
    mpid INT NOT NULL,
    PRIMARY KEY (uemail, mpid),
    FOREIGN KEY (uemail) REFERENCES User(email)
        ON DELETE CASCADE,
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
        ON DELETE CASCADE
);

CREATE TABLE Movie(
    mpid INT NOT NULL PRIMARY KEY,
    boxoffice_collection INT,
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
        ON DELETE CASCADE
);

CREATE TABLE Series(
    mpid INT NOT NULL PRIMARY KEY,
    season_count INT,
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
        ON DELETE CASCADE
);
CREATE TABLE People (
    id INT NOT NULL PRIMARY KEY,   
    name VARCHAR(100),   
    nationality VARCHAR(100),   
    dob DATE,   
    gender VARCHAR(1) 
);

CREATE TABLE Role(
     mpid int NOT NULL, 
     pid int NOT NULL,
     role_name varchar(100) NOT NULL,
     PRIMARY KEY (mpid, pid, role_name),
     FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
        ON DELETE CASCADE,
     FOREIGN KEY (pid) REFERENCES People(id)
         ON DELETE CASCADE
     );

create table Award(
    mpid int not null,  
    pid int not null, 
    award_name varchar(100) not null,  
    award_year int not null,
    Primary key(mpid, pid, award_name, award_year),
    foreign key (mpid) references motionpicture(id) 
    on delete cascade,
    foreign key (pid) references people(id) 
    on delete cascade );

CREATE TABLE Genre(
    mpid int NOT NULL,
    genre_name varchar(100) NOT NULL,
    PRIMARY KEY (mpid, genre_name),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
        ON DELETE CASCADE
    );

CREATE TABLE Location(
    mpid INT NOT NULL UNIQUE,
    zip INT NOT NULL,
    city varchar(100),
    country varchar(100),
    PRIMARY KEY(mpid, zip),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
        ON DELETE CASCADE
    );
