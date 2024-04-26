CREATE TABLE Users (
    id        INTEGER PRIMARY KEY,
    email     TEXT NOT NULL UNIQUE,
    name      TEXT NOT NULL
);
CREATE TABLE Listings (
    id          INTEGER PRIMARY KEY,
    userId      INTEGER NOT NULL,
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (userId) REFERENCES Users(id) ON DELETE CASCADE
);
CREATE TABLE ADDRESS (
    id          INTEGER PRIMARY KEY,
    listingId   INTEGER NOT NULL,
    x           INTEGER NOT NULL CHECK (day BETWEEN 1 AND 100),
    y           INTEGER NOT NULL CHECK (day BETWEEN 1 AND 100),
    FOREIGN KEY (listingId) REFERENCES Listings(id) ON DELETE CASCADE
);


CREATE TABLE Reservations (
    id         INTEGER PRIMARY KEY,
    listingId  INTEGER NOT NULL,
    userId     INTEGER NOT NULL,
    day        INTEGER NOT NULL CHECK (day BETWEEN 1 AND 100),
    FOREIGN KEY (listingId) REFERENCES Listings(id) ON DELETE CASCADE,
    FOREIGN KEY (userId) REFERENCES Users(id) ON DELETE CASCADE
);
CREATE TABLE Reviews (
    id         INTEGER PRIMARY KEY,
    listingId  INTEGER NOT NULL,
    userId     INTEGER NOT NULL,
    rating     INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    text       TEXT NOT NULL,
    FOREIGN KEY (listingId) REFERENCES Listings(id) ON DELETE CASCADE,
    FOREIGN KEY (userId) REFERENCES Users(id)
);
