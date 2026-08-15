import sqlite3

# OPOMBA: VSI REZULTATI SO 2015-2025 BREZ LETA 2020, SAJ JE BILO
# TEKMOVANJE, ZARADI KORONE, ODPOVEDANO


def povezava_baza():
    conn = sqlite3.connect("planica.db")
    return conn


# 1. Funkcija za iskanje tekmovalca
def poisci_tekmovalca():
    """Funkcija glede na ustvarjeno bazo podatkov poišče informacije
        o izbranem tekmovalecu."""

    leto = input("Vnesi leto: ")
    ime = input("Vnesi ime: ").strip()
    priimek = input("Vnesi priimek: ").strip()

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        t.ime,
        t.priimek,
        t.drzava,
        r.mesto,
        r.skok_1,
        r.skok_2
    FROM rezultati r
    JOIN tekmovalci t
    ON r.tekmovalec_id = t.id
    WHERE r.leto = ?
    AND LOWER(t.ime) = LOWER(?)
    AND LOWER(t.priimek) = LOWER(?)
    """,
                (leto, ime, priimek))

    rezultat = cur.fetchone()

    if rezultat:
        print("\nRezultat:")
        print("----------------")
        print("Tekmovalec:", rezultat[0], rezultat[1])
        print("Država:", rezultat[2])
        print("Mesto:", rezultat[3])
        print("Skok 1:", rezultat[4], "m")
        print("Skok 2:", rezultat[5], "m")
    else:
        print(f"\n{ime} {priimek} v letu {leto} ni nastopal.")

    conn.close()

# 2. Funkcija za izpis celotne lestvice


def lestvica_leto():
    """Glede na vnešeno letnico, funkcija vrne celotno končno lestvico
        rezultatov za izbrano leto."""

    leto = input("Vnesi leto: ")

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        r.mesto,
        t.ime,
        t.priimek,
        t.drzava,
        r.skok_1,
        r.skok_2
    FROM rezultati r
    JOIN tekmovalci t
    ON r.tekmovalec_id = t.id
    WHERE r.leto = ?
    ORDER BY r.mesto
    """, (leto,))

    rezultati = cur.fetchall()

    if rezultati:

        print(f"\nPLANICA {leto}")
        print("-" * 60)

        for r in rezultati:
            print(
                f"{r[0]}. {r[1]} {r[2]} ({r[3]}) "
                f"| {r[4]} m | {r[5]} m"
            )

    else:
        print("Za to leto ni podatkov.")

    conn.close()


# 3. Prikaz nastopov posameznika
def nastopi_tekmovalca():
    """Funkcija vrne vse nastope v Planici za izbranega tekmovalca."""

    ime = input("Vnesi ime: ").strip()
    priimek = input("Vnesi priimek: ").strip()

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        r.leto,
        r.mesto,
        r.skok_1,
        r.skok_2
    FROM rezultati r
    JOIN tekmovalci t
    ON r.tekmovalec_id = t.id
    WHERE LOWER(t.ime)=LOWER(?)
    AND LOWER(t.priimek)=LOWER(?)
    ORDER BY r.leto
    """, (ime, priimek))

    rezultati = cur.fetchall()

    if rezultati:
        print(f"\n{ime} {priimek}")
        print("-"*40)

        for leto, mesto, skok1, skok2 in rezultati:
            print(
                leto,
                "| mesto:",
                mesto,
                "   |",
                skok1,
                "m ,",
                skok2,
                "m"
            )
    else:
        print("Tekmovalec ni najden.")

    conn.close()


# 4. Statistika tekmovalca
def statistika_tekmovalca():
    """Funkcija vrne število nastopov, najboljšo uvrstitev, povprečno
        uvrstitev ter najdaljši skok med 2015-2025."""

    ime = input("Vnesi ime: ").strip()
    priimek = input("Vnesi priimek: ").strip()

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        COUNT(*),
        MIN(r.mesto),
        AVG(r.mesto),
        MAX(r.skok_1, r.skok_2)
    FROM rezultati r
    JOIN tekmovalci t
    ON r.tekmovalec_id = t.id
    WHERE LOWER(t.ime)=LOWER(?)
    AND LOWER(t.priimek)=LOWER(?)
    """, (ime, priimek))

    rezultat = cur.fetchone()

    if rezultat[0] > 0:
        print(f"\nStatistika: {ime} {priimek}")
        print("-"*40)
        print("Število nastopov:", rezultat[0])
        print("Najboljša uvrstitev:", rezultat[1])
        print("Povprečna uvrstitev:", round(rezultat[2], 2))

        # najdaljši skok posebej izračunamo
        cur.execute("""
        SELECT MAX(skok)
        FROM (
            SELECT skok_1 AS skok
            FROM rezultati r
            JOIN tekmovalci t
            ON r.tekmovalec_id=t.id
            WHERE LOWER(t.ime)=LOWER(?)
            AND LOWER(t.priimek)=LOWER(?)

            UNION

            SELECT skok_2 AS skok
            FROM rezultati r
            JOIN tekmovalci t
            ON r.tekmovalec_id=t.id
            WHERE LOWER(t.ime)=LOWER(?)
            AND LOWER(t.priimek)=LOWER(?)
        )
        """, (ime, priimek, ime, priimek))

        najdaljsi = cur.fetchone()[0]

        print("Najdaljši skok:", najdaljsi, "m")

    else:
        print("Tekmovalec ni najden.")

    conn.close()


# 5. Tekmovalci izbrane države
def tekmovalci_drzava():
    """Funkcija vrne vse tekmovalce, ki so v Planici zastopali
        izbrano državo."""

    drzava = input("Vnesi državo (npr. SLO): ").strip()

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
    SELECT DISTINCT ime, priimek
    FROM tekmovalci
    WHERE UPPER(drzava)=UPPER(?)
    ORDER BY priimek
    """, (drzava,))

    tekmovalci = cur.fetchall()

    if tekmovalci:
        print(f"\nTekmovalci države {drzava}:")
        print("-"*30)

        for t in tekmovalci:
            print(t[0], t[1])

    else:
        print("Za to državo ni tekmovalcev.")

    conn.close()


# 6. Vsi zmagovalci planice 2015-2025
def zmagovalci_po_letih():
    """Funkcija vrne vse zmagovalce za leta 2015-2025."""

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        r.leto,
        t.ime,
        t.priimek,
        t.drzava
    FROM rezultati r
    JOIN tekmovalci t
    ON r.tekmovalec_id = t.id
    WHERE r.mesto = 1
    ORDER BY r.leto
    """)

    zmagovalci = cur.fetchall()

    print("\n===== ZMAGOVALCI PLANICE =====")
    print("-" * 50)
    print("Leto | Zmagovalec | Država")
    print("-" * 50)

    for leto, ime, priimek, drzava in zmagovalci:
        print(
            leto,
            "|",
            ime,
            priimek,
            "|",
            drzava
        )

    conn.close()


# Menu
while True:

    print("""
===== PLANICA =====

1 - Poišči rezultat tekmovalca za izbrano leto
2 - Prikaži lestvico izbranega leta
3 - Prikaži vse nastope tekmovalca
4 - Statistika tekmovalca
5 - Prikaži tekmovalce izbrane države
6 - Zmagovalci planice 2015-2025
7 - Izhod

""")

    izbira = input("Izbira: ")

    if izbira == "1":
        poisci_tekmovalca()

    elif izbira == "2":
        lestvica_leto()

    elif izbira == "3":
        nastopi_tekmovalca()

    elif izbira == "4":
        statistika_tekmovalca()

    elif izbira == "5":
        tekmovalci_drzava()

    elif izbira == "6":
        zmagovalci_po_letih()

    elif izbira == "7":
        print("Nasvidenje!")
        break

    else:
        print("Neveljavna izbira.")