import sqlite3

DB_FILE = "data.db"

db = sqlite3.connect(DB_FILE)
c = db.cursor()

c.executescript("""
    DROP TABLE IF EXISTS DefaultPassengers;
    CREATE TABLE DefaultPassengers (
        id INTEGER PRIMARY KEY,
        survived INTEGER,
        class INTEGER,
        name TEXT,
        sex TEXT,
        age INTEGER,
        fare REAL,
        isAlone INTEGER,
        cabin TEXT,
        port TEXT
    );

    DROP TABLE IF EXISTS Games;
    CREATE TABLE Games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        currLocation TEXT,
        charisma INTEGER DEFAULT 40,
        moves INTEGER DEFAULT 200,
        active INTEGER DEFAULT TRUE,
        FOREIGN KEY (username) REFERENCES Users(username)
    );

    DROP TABLE IF EXISTS Passengers;
    CREATE TABLE Passengers (
        game INTEGER,
        id INTEGER,
        room TEXT,
        age INTEGER,
        class INTEGER,
        FOREIGN KEY (game) REFERENCES Games(id),
        FOREIGN KEY (id) REFERENCES DefaultPassengers(id)
    );

    DROP TABLE IF EXISTS Rooms;
    CREATE TABLE Rooms (
        game INTEGER,
        usedCapacity INTEGER DEFAULT 0,
        room TEXT,
        FOREIGN KEY (game) REFERENCES Games(id)
    );

    DROP TABLE IF EXISTS Items;
    CREATE TABLE Items (
        name TEXT,
        game INTEGER,
        amount INTEGER,
        FOREIGN KEY (game) REFERENCES Games(id)
    );

    DROP TABLE IF EXISTS Users;
    CREATE TABLE Users (
        username TEXT PRIMARY KEY,
        password TEXT
    );
""")

db.commit()
db.close()
