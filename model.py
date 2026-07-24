import sqlite3


def povezava_baza():
    """
    Ustvari povezavo z SQLite bazo.
    """
    conn = sqlite3.connect("planica.db")
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------------------------
# TEKMOVALCI IN REZULTATI
# -------------------------------------------------

def moznosti_izbire():
    """
    Vrne podatke za spustne sezname v spletni aplikaciji.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT leto
        FROM rezultati
        ORDER BY leto
    """)
    leta = [vrstica[0] for vrstica in cur.fetchall()]

    cur.execute("""
        SELECT id, ime, priimek, drzava
        FROM tekmovalci
        ORDER BY priimek, ime
    """)
    tekmovalci = cur.fetchall()

    cur.execute("""
        SELECT DISTINCT drzava
        FROM tekmovalci
        ORDER BY drzava
    """)
    drzave = [vrstica[0] for vrstica in cur.fetchall()]

    conn.close()

    return {
        "leta": leta,
        "tekmovalci_za_izbiro": tekmovalci,
        "drzave": drzave
    }


def tekmovalec_po_id(tekmovalec_id):
    """
    Vrne podatke o tekmovalcu glede na id.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, ime, priimek, drzava
        FROM tekmovalci
        WHERE id = ?
    """, (tekmovalec_id,))

    tekmovalec = cur.fetchone()

    conn.close()

    return tekmovalec


def rezultat_tekme(leto, tekmovalec_id):
    """
    Vrne rezultat tekmovalca na izbranem tekmovanju.
    """

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
        AND t.id = ?
    """, (leto, tekmovalec_id))

    rezultat = cur.fetchone()

    conn.close()

    return rezultat


def lestvica(leto):
    """
    Vrne lestvico za izbrano leto.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            r.mesto,
            t.id AS tekmovalec_id,
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

    conn.close()

    return rezultati


def profil_tekmovalca(tekmovalec_id=None, ime=None, priimek=None):
    """
    Vrne vse nastope izbranega tekmovalca.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    query = """
        SELECT
            t.id AS tekmovalec_id,
            t.ime,
            t.priimek,
            t.drzava,
            r.leto,
            r.mesto,
            r.skok_1,
            r.skok_2

        FROM rezultati r

        JOIN tekmovalci t
        ON r.tekmovalec_id = t.id
    """

    if tekmovalec_id is not None:
        query += """
            WHERE t.id = ?
        """
        parametri = (tekmovalec_id,)

    else:
        query += """
            WHERE LOWER(t.ime)=LOWER(?)
            AND LOWER(t.priimek)=LOWER(?)
        """
        parametri = (ime, priimek)

    query += """
        ORDER BY r.leto
    """

    cur.execute(query, parametri)

    rezultat = cur.fetchall()

    conn.close()

    return rezultat


def statistika(ime, priimek):
    """
    Vrne osnovno statistiko tekmovalca.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*),
            MIN(r.mesto),
            AVG(r.mesto)

        FROM rezultati r

        JOIN tekmovalci t
        ON r.tekmovalec_id = t.id

        WHERE LOWER(t.ime)=LOWER(?)
        AND LOWER(t.priimek)=LOWER(?)
    """, (ime, priimek))

    rezultat = cur.fetchone()

    conn.close()

    return rezultat


def podatki_graf(ime, priimek):
    """
    Vrne podatke za graf uspešnosti tekmovalca.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            r.leto,
            r.mesto

        FROM rezultati r

        JOIN tekmovalci t
        ON r.tekmovalec_id = t.id

        WHERE LOWER(t.ime)=LOWER(?)
        AND LOWER(t.priimek)=LOWER(?)

        ORDER BY r.leto
    """, (ime, priimek))

    podatki = cur.fetchall()

    conn.close()

    return podatki


def tekmovalci_drzava(drzava):
    """
    Vrne vse tekmovalce iz izbrane države.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT
            id AS tekmovalec_id,
            ime,
            priimek,
            drzava

        FROM tekmovalci

        WHERE LOWER(drzava)=LOWER(?)

        ORDER BY priimek
    """, (drzava,))

    rezultat = cur.fetchall()

    conn.close()

    return rezultat


def zmagovalci():
    """
    Vrne zmagovalce vseh let.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            r.leto,
            t.id AS tekmovalec_id,
            t.ime,
            t.priimek,
            t.drzava

        FROM rezultati r

        JOIN tekmovalci t
        ON r.tekmovalec_id=t.id

        WHERE r.mesto=1

        ORDER BY r.leto
    """)

    rezultat = cur.fetchall()

    conn.close()

    return rezultat

# -------------------------------------------------
# UPORABNIKI
# -------------------------------------------------

def dodaj_uporabnika(uporabnisko_ime, geslo):
    """
    Doda novega uporabnika v bazo.
    Vrne True, če je registracija uspešna,
    oziroma False, če uporabniško ime že obstaja.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO uporabniki
            (uporabnisko_ime, geslo)

            VALUES (?, ?)
        """, (uporabnisko_ime, geslo))

        conn.commit()
        uspeh = True

    except sqlite3.IntegrityError:
        uspeh = False

    conn.close()

    return uspeh


def preveri_uporabnika(uporabnisko_ime, geslo):
    """
    Preveri prijavo uporabnika.
    Vrne uporabnika, če sta podatka pravilna.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, uporabnisko_ime
        FROM uporabniki

        WHERE uporabnisko_ime = ?
        AND geslo = ?
    """, (uporabnisko_ime, geslo))

    uporabnik = cur.fetchone()

    conn.close()

    return uporabnik


# -------------------------------------------------
# KOMENTARJI
# -------------------------------------------------

def dodaj_komentar(uporabnik_id, vsebina):
    """
    Shrani nov komentar uporabnika.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO komentarji
        (uporabnik_id, vsebina, datum)

        VALUES (?, ?, datetime('now'))
    """, (uporabnik_id, vsebina))

    conn.commit()
    conn.close()


def pridobi_komentarje():
    """
    Vrne vse komentarje skupaj z uporabniškimi imeni.
    """

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            komentarji.vsebina,
            komentarji.datum,
            uporabniki.uporabnisko_ime

        FROM komentarji

        JOIN uporabniki
        ON komentarji.uporabnik_id = uporabniki.id

        ORDER BY komentarji.id DESC
    """)

    komentarji = cur.fetchall()

    conn.close()

    return komentarji