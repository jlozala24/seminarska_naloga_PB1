import sqlite3
import pandas as pd
import glob
import os

# Ustvari povezavo z bazo
conn = sqlite3.connect("planica.db")
cur = conn.cursor()

# Izbriši stare tabele, če že obstajajo
cur.execute("DROP TABLE IF EXISTS rezultati")
cur.execute("DROP TABLE IF EXISTS tekmovalci")

# Ustvari tabelo tekmovalcev
cur.execute("""
CREATE TABLE tekmovalci (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    drzava TEXT NOT NULL,
    UNIQUE(ime, priimek, drzava)
)
""")

# Ustvari tabelo rezultatov
cur.execute("""
CREATE TABLE rezultati (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tekmovalec_id INTEGER NOT NULL,
    leto INTEGER NOT NULL,
    mesto INTEGER NOT NULL,
    skok_1 REAL,
    skok_2 REAL,
    FOREIGN KEY(tekmovalec_id) REFERENCES tekmovalci(id)
)
""")

# Tabela uporabnikov
cur.execute("""
CREATE TABLE uporabniki (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uporabnisko_ime TEXT UNIQUE NOT NULL,
    geslo TEXT NOT NULL
)
""")

# Tabela komentarjev
cur.execute("""
CREATE TABLE komentarji (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uporabnik_id INTEGER NOT NULL,
    vsebina TEXT NOT NULL,
    datum TEXT NOT NULL,
    FOREIGN KEY(uporabnik_id) REFERENCES uporabniki(id)
)
""")

# Preberi vse CSV datoteke
for datoteka in sorted(glob.glob("csv/planica_*.csv")):

    # Iz imena datoteke dobi leto
    leto = int(os.path.basename(datoteka).split("_")[1].split(".")[0])

    df = pd.read_csv(datoteka)

    # Odstrani odvečne presledke v imenih stolpcev
    df.columns = df.columns.str.strip()

    for _, vrstica in df.iterrows():

        ime = str(vrstica["Ime"]).strip()
        priimek = str(vrstica["Priimek"]).strip()
        drzava = str(vrstica["Drzava"]).strip()

        # Dodaj tekmovalca, če ga še ni
        # Če je tekmovalec že dodan preskoči en id, zato vmes 30 in nato 35 namesto 30 in 31
        cur.execute("""
            INSERT OR IGNORE INTO tekmovalci
            (ime, priimek, drzava)
            VALUES (?, ?, ?)
        """, (ime, priimek, drzava))

        # Poišči njegov ID
        cur.execute("""
            SELECT id
            FROM tekmovalci
            WHERE ime=? AND priimek=? AND drzava=?
        """, (ime, priimek, drzava))

        tekmovalec_id = cur.fetchone()[0]

        # Dodaj rezultat
        cur.execute("""
            INSERT INTO rezultati
            (tekmovalec_id, leto, mesto, skok_1, skok_2)
            VALUES (?, ?, ?, ?, ?)
        """, (
            tekmovalec_id,
            leto,
            int(vrstica["Mesto"]),
            float(vrstica["Skok_1"]),
            float(vrstica["Skok_2"])
        ))

conn.commit()
conn.close()

print("Baza planica.db je bila uspešno ustvarjena.")