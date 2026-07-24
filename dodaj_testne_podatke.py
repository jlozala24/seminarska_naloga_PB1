import sqlite3

conn = sqlite3.connect("planica.db")
cur = conn.cursor()

# -----------------------
# uporabniki
# -----------------------

uporabniki = [
    ("zala", "1234"),
    ("manca", "geslo123"),
    ("katarina", "planica"),
    ("vid", "skoki")
]

for uporabnisko_ime, geslo in uporabniki:
    cur.execute("""
    INSERT OR IGNORE INTO uporabniki
    (uporabnisko_ime, geslo)
    VALUES (?, ?)
    """, (uporabnisko_ime, geslo))

# -----------------------
# komentarji
# -----------------------

komentarji = [
    (1, "Planica je vedno vrhunec sezone!"),
    (2, "Upam na slovensko zmago prihodnje leto."),
    (3, "Najlepša skakalnica na svetu."),
    (4, "Komaj čakam naslednje polete!")
]

for uporabnik_id, vsebina in komentarji:
    cur.execute("""
    INSERT INTO komentarji
    (uporabnik_id, vsebina, datum)
    VALUES (?, ?, datetime('now'))
    """, (uporabnik_id, vsebina))

conn.commit()
conn.close()

print("Testni uporabniki in komentarji dodani.")