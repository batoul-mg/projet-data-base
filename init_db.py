import sqlite3

conn = sqlite3.connect('hotel.db')
c = conn.cursor()

# Création des tables

c.execute('''
CREATE TABLE IF NOT EXISTS Ville (
    IdVille INTEGER PRIMARY KEY,
    NomVille TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Hotel (
    IdHotel INTEGER PRIMARY KEY,
    NomHotel TEXT,
    IdVille INTEGER,
    Adresse TEXT,
    FOREIGN KEY (IdVille) REFERENCES Ville(IdVille)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Client (
    IdClient INTEGER PRIMARY KEY,
    Nom TEXT,
    Adresse TEXT,
    Ville TEXT,
    Code_postal INTEGER,
    Email TEXT UNIQUE,
    NumTel TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS TypeChambre (
    IdType INTEGER PRIMARY KEY,
    Type TEXT,
    Tarif REAL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Chambre (
    IdChambre INTEGER PRIMARY KEY,
    numero INTEGER,
    Etage INTEGER,
    est_reserve BOOLEAN,
    IdHotel INTEGER,
    IdType INTEGER,
    FOREIGN KEY (IdHotel) REFERENCES Hotel(IdHotel),
    FOREIGN KEY (IdType) REFERENCES TypeChambre(IdType)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Prestation (
    IdPrestation INTEGER PRIMARY KEY,
    Prix REAL,
    Description TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Reservation (
    IdReservation INTEGER PRIMARY KEY,
    DateArrivee DATE,
    DateDepart DATE,
    IdClient INTEGER,
    IdChambre INTEGER,
    FOREIGN KEY (IdClient) REFERENCES Client(IdClient),
    FOREIGN KEY (IdChambre) REFERENCES Chambre(IdChambre)
)
''')

def charger_evaluations():
    c.execute("""
        SELECT e.IdEvaluation, c.Nom, e.note, e.Text_desc, e.Date_arrivee
        FROM Evaluation e
        JOIN Client c ON e.IdClient = c.IdClient
        ORDER BY e.Date_arrivee DESC
    """)
    return c.fetchall()



conn.commit()
conn.close()
print("✅ Tables créées avec succès !")
