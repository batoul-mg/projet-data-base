import sqlite3

conn = sqlite3.connect('hotel.db')
c = conn.cursor()

# Création des tables
c.execute('''
CREATE TABLE IF NOT EXISTS Ville (
    IdVille INTEGER PRIMARY KEY,
    NomVille TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Hotel (
    IdHotel INTEGER PRIMARY KEY,
    NomHotel TEXT NOT NULL,
    IdVille INTEGER,
    Adresse TEXT,
    FOREIGN KEY(IdVille) REFERENCES Ville(IdVille)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Client (
    IdClient INTEGER PRIMARY KEY,
    Nom TEXT NOT NULL,
    Adresse TEXT,
    Ville TEXT,
    CodePostal INTEGER,
    Email TEXT,
    Telephone TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS TypeChambre (
    IdType INTEGER PRIMARY KEY,
    Type TEXT NOT NULL,
    Prix INTEGER NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Chambre (
    IdChambre INTEGER PRIMARY KEY,
    Numero INTEGER NOT NULL,
    Disponible INTEGER,
    Fumeur INTEGER,
    IdHotel INTEGER,
    IdType INTEGER,
    FOREIGN KEY(IdHotel) REFERENCES Hotel(IdHotel),
    FOREIGN KEY(IdType) REFERENCES TypeChambre(IdType)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Prestation (
    IdPrestation INTEGER PRIMARY KEY,
    Prix INTEGER,
    Description TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Reservation (
    IdReservation INTEGER PRIMARY KEY,
    DateArrivee TEXT,
    DateDepart TEXT,
    IdClient INTEGER,
    IdChambre INTEGER,
    FOREIGN KEY(IdClient) REFERENCES Client(IdClient),
    FOREIGN KEY(IdChambre) REFERENCES Chambre(IdChambre)
)
''')
c.execute("DROP TABLE IF EXISTS Evaluation")
c.execute('''
CREATE TABLE IF NOT EXISTS Evaluation (
    IdEvaluation INTEGER PRIMARY KEY,
    DateEvaluation TEXT,
    Note INTEGER,
    Commentaire TEXT,
    IdReservation INTEGER,
    IdClient INTEGER,
    FOREIGN KEY(IdReservation) REFERENCES Reservation(IdReservation),
    FOREIGN KEY(IdClient) REFERENCES Client(IdClient)
)
''')
c.execute("DELETE FROM Ville")
# Insertion des données
c.executemany("INSERT INTO Ville (IdVille, NomVille) VALUES (?, ?)", [
    (1, 'Marrakech'), (2, 'Tanger'), (3, 'Rabat'), (4, 'Casablanca'), (5, 'Fès')
])
c.execute("DELETE FROM Hotel")
c.executemany("INSERT INTO Hotel (IdHotel, NomHotel, IdVille, Adresse) VALUES (?, ?, ?, ?)", [
    (1, 'Hotel Atlas Marrakech', 1, 'Rue de la Kasbah, Marrakech'),
    (2, 'Hotel Medina Tanger', 2, 'Avenue Mohamed VI, Tanger'),
    (3, 'Hotel Royal Rabat', 3, 'Boulevard Hassan II, Rabat'),
    (4, 'Hotel Anfa Casablanca', 4, 'Corniche, Casablanca'),
    (5, 'Hotel Fès El Bali', 5, 'Medina, Fès')
])
c.execute("DELETE FROM Client")
c.executemany("INSERT INTO Client VALUES (?, ?, ?, ?, ?, ?, ?)", [
    (1, 'Ahmed Benali', '12 Rue Jamaa El Fna', 'Marrakech', 40000, 'ahmed.benali@mail.ma', '0601234567'),
    (2, 'Fatima Zahra', '45 Avenue Mohammed V', 'Rabat', 10000, 'fatima.zahra@mail.ma', '0602345678'),
    (3, 'Youssef Idrissi', '23 Rue de Tanger', 'Tanger', 90000, 'youssef.idrissi@mail.ma', '0603456789'),
    (4, 'Khadija El Fassi', '18 Place Nejjarine', 'Fès', 30000, 'khadija.elfassi@mail.ma', '0604567890'),
    (5, 'Mohamed Amrani', "50 Boulevard d'Anfa", 'Casablanca', 20000, 'mohamed.amrani@mail.ma', '0605678901')
])
c.execute("DELETE FROM TypeChambre")
c.executemany("INSERT INTO TypeChambre VALUES (?, ?, ?)", [
    (1, 'Simple', 350), (2, 'Double', 550), (3, 'Suite', 1000)
])
c.execute("DELETE FROM Chambre")
c.executemany("INSERT INTO Chambre VALUES (?, ?, ?, ?, ?, ?)", [
    (1, 101, 0, 0, 1, 1), (2, 102, 0, 0, 1, 2), (3, 201, 1, 1, 2, 1),
    (4, 202, 1, 0, 2, 3), (5, 301, 2, 0, 3, 2), (6, 302, 2, 0, 3, 3),
    (7, 401, 3, 1, 4, 1), (8, 402, 3, 0, 4, 2), (9, 501, 4, 0, 5, 3)
])
c.execute("DELETE FROM Prestation")
c.executemany("INSERT INTO Prestation VALUES (?, ?, ?)", [
    (1, 50, 'Petit-déjeuner'), (2, 100, 'Navette aéroport'),
    (3, 0, 'Wi-Fi gratuit'), (4, 200, 'Spa et bien-être'), (5, 80, 'Parking sécurisé')
])
c.execute("DELETE FROM Reservation")
c.executemany("INSERT INTO Reservation VALUES (?, ?, ?, ?, ?)", [
    (1, '2025-06-15', '2025-06-18', 1, 1),
    (2, '2025-07-01', '2025-07-05', 2, 3),
    (3, '2025-08-10', '2025-08-14', 3, 4),
    (4, '2025-09-05', '2025-09-07', 4, 5),
    (5, '2025-09-20', '2025-09-25', 5, 9)
])
c.execute("DELETE FROM Evaluation")
c.executemany("INSERT INTO Evaluation VALUES (?, ?, ?, ?, ?, ?)", [
    (1, '2025-06-18', 5, 'Excellent séjour à Marrakech!', 1, 1),
    (2, '2025-07-05', 4, 'Hotel confortable à Tanger.', 2, 2),
    (3, '2025-08-14', 3, 'Correct mais un peu bruyant.', 3, 3),
    (4, '2025-09-07', 5, 'Personnel très accueillant.', 4, 4),
    (5, '2025-09-25', 4, 'Très bon rapport qualité/prix.', 5, 5)
])

conn.commit()
conn.close()

print("✅ Données insérées avec succès dans hotel.db !")
