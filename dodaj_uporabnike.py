import sqlite3

# Novi prazni tabeli za uporabnike in komentarje (prvotna za ustvarit bazo
# dela in nisem želela spreminjati, da slučajno kej ne bi delalo).

conn = sqlite3.connect("planica.db")

cur = conn.cursor()


# tabela uporabnikov
cur.execute("""
CREATE TABLE IF NOT EXISTS uporabniki (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    uporabnisko_ime TEXT UNIQUE NOT NULL,

    geslo TEXT NOT NULL

)
""")


# tabela komentarjev
cur.execute("""
CREATE TABLE IF NOT EXISTS komentarji (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    uporabnik_id INTEGER NOT NULL,

    komentar TEXT NOT NULL,

    datum TEXT,

    FOREIGN KEY (uporabnik_id)
    REFERENCES uporabniki(id)

)
""")


conn.commit()

conn.close()


print("Tabeli uporabniki in komentarji sta bili uspešno ustvarjeni.")