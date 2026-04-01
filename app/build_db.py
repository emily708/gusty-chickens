import sqlite3

DB_FILE = "data.db"

db = sqlite3.connect(DB_FILE)
c = db.cursor()

c.executescript("""
    DROP TABLE IF EXISTS DefaultRooms;
    CREATE TABLE DefaultRooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        capacity INTEGER
    );

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
        currLocation INTEGER,
        charisma INTEGER DEFAULT 40,
        moves INTEGER DEFAULT 200,
        active INTEGER DEFAULT TRUE,
        FOREIGN KEY (username) REFERENCES Users(username),
        FOREIGN KEY (currLocation) REFERENCES DefaultRooms(id)
    );

    DROP TABLE IF EXISTS Passengers;
    CREATE TABLE Passengers (
        game INTEGER,
        id INTEGER,
        room INTEGER,
        FOREIGN KEY (game) REFERENCES Games(id),
        FOREIGN KEY (id) REFERENCES DefaultPassengers(id),
        FOREIGN KEY (room) REFERENCES DefaultRooms(id)
    );

    DROP TABLE IF EXISTS Items;
    CREATE TABLE Items (
        name TEXT,
        game INTEGER,
        FOREIGN KEY (game) REFERENCES Games(id)
    );
""")

db.commit()
db.close()
