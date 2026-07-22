from flask import Flask, render_template, request, session, redirect
import sqlite3

# Flask je pythonova knjižnica za izdelavo spletnih aplikacij
app = Flask(__name__)
# ta key potrebuje za shranjevanje session podatkov
# da ve kdo je prijavljen
app.secret_key = "planica skrivnost"


# -------------------------------------------------
#           FUNKCIJE Z SQL POIZVEDBAMI
# -------------------------------------------------

# povezava baze do vsake od naslednjih funkcij
def povezava_baza():
    conn = sqlite3.connect("planica.db")
    conn.row_factory = sqlite3.Row
    return conn

# Funkcija, ki z SQL poizvedbo dobi rezultate za iskano leto
def lestvica(leto):

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

    conn.close()

    return rezultati


# Funkcija, ki preko SQL naredi poizvedbo o vseh skokih v planici za izbranega tekmovalca
def profil_tekmovalca(ime, priimek):

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        t.ime,
        t.priimek,
        t.drzava,
        r.leto,
        r.mesto,
        r.skok_1,
        r.skok_2

    FROM rezultati r

    JOIN tekmovalci t
    ON r.tekmovalec_id=t.id

    WHERE LOWER(t.ime)=LOWER(?)
    AND LOWER(t.priimek)=LOWER(?)

    ORDER BY r.leto

    """, (ime, priimek))


    podatki = cur.fetchall()

    conn.close()

    return podatki

# Funkcija z SQL poizvedbo dobi število nastopov, najboljši 
# in povprečen dosežek za posameznega tekmovalca
def statistika(ime, priimek):

    conn=povezava_baza()
    cur=conn.cursor()

    cur.execute("""
    SELECT
        COUNT(*),
        MIN(r.mesto),
        AVG(r.mesto)

    FROM rezultati r

    JOIN tekmovalci t
    ON r.tekmovalec_id=t.id

    WHERE LOWER(t.ime)=LOWER(?)
    AND LOWER(t.priimek)=LOWER(?)

    """,(ime,priimek))


    rezultat=cur.fetchone()

    conn.close()

    return rezultat

# Graf na spletni strani statistike tekmovalca
def podatki_graf(ime, priimek):

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        r.leto,
        r.mesto

    FROM rezultati r

    JOIN tekmovalci t
    ON r.tekmovalec_id=t.id

    WHERE LOWER(t.ime)=LOWER(?)
    AND LOWER(t.priimek)=LOWER(?)

    ORDER BY r.leto

    """, (ime, priimek))


    podatki = cur.fetchall()

    conn.close()

    return podatki


# Funkcija z SQL pridobi vse tekmovalce za iskano državo
def tekmovalci_drzava(drzava):

    conn = povezava_baza()
    cur = conn.cursor()

    cur.execute("""
    SELECT DISTINCT
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


# Funkcija z SQL poizvedbo vrne tabelo vseh zmagovalcev 2015-2025
def zmagovalci():

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
    ON r.tekmovalec_id=t.id

    WHERE r.mesto=1

    ORDER BY r.leto

    """)


    rezultat = cur.fetchall()

    conn.close()

    return rezultat

# Za vsak komentar v bazi dodati id uporabnika, ki ga
# z SQL poizvedbo najde v tabeli uporabniki
def pridobi_komentarje():

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
    

# ------------------------------------------------
#               SPLETNE "POTI" 
# ------------------------------------------------

# Domača stran
@app.route("/")
def domov():

    return render_template("index.html")

# Iskanje rezultatov
@app.route("/iskanje", methods=["GET", "POST"])
def iskanje():

    rezultat = None

    if request.method == "POST":

        leto = request.form["leto"]
        ime = request.form["ime"]
        priimek = request.form["priimek"]

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
        AND LOWER(t.ime)=LOWER(?)
        AND LOWER(t.priimek)=LOWER(?)

        """, (leto, ime, priimek))


        rezultat = cur.fetchone()

        conn.close()


    return render_template(
        "iskanje.html",
        rezultat=rezultat
    )


# Lestvica - meni
@app.route("/lestvica", methods=["GET", "POST"])
def stran_lestvica():

    rezultati = None
    leto = None

    if request.method == "POST":

        leto = request.form["leto"]

        rezultati = lestvica(leto)


    return render_template(
        "lestvica.html",
        rezultati=rezultati,
        leto=leto
    )
    
    
# profil - meni 
@app.route("/profil", methods=["GET","POST"])
def profil():

    rezultati = None
    ime = ""
    priimek = ""
    sporocilo = ""

    if request.method == "POST":

        ime = request.form["ime"]
        priimek = request.form["priimek"]

        rezultati = profil_tekmovalca(ime, priimek)
        
        if len(rezultati) == 0:
            sporocilo = f"{ime} {priimek} ni nastopal v Planici med letoma 2015 in 2025."


    return render_template(
        "profil.html",
        rezultati=rezultati,
        ime=ime,
        priimek=priimek
    )
    

# statistika - meni     
@app.route("/statistika", methods=["GET","POST"])
def stran_statistika():

    sporocilo = ""
    rezultat=None
    graf=None

    if request.method=="POST":

        ime=request.form["ime"]
        priimek=request.form["priimek"]

        rezultat=statistika(ime,priimek)
        if rezultat[0] == 0:
            sporocilo = f"{ime} {priimek} ni nastopal v Planici med letoma 2015 in 2025."
        graf=podatki_graf(ime,priimek)


    return render_template(
        "statistika.html",
        rezultat=rezultat,
        sporocilo=sporocilo,
        graf=graf
    )


# država - meni
@app.route("/drzava", methods=["GET", "POST"])
def drzava():

    tekmovalci = None

    if request.method == "POST":

        drzava = request.form["drzava"]

        tekmovalci = tekmovalci_drzava(drzava)


    return render_template(
        "drzava.html",
        tekmovalci=tekmovalci
    )
    
    
# zmagovalci - meni  
@app.route("/zmagovalci")
def stran_zmagovalci():

    rezultat = zmagovalci()

    return render_template(
        "zmagovalci.html",
        rezultat=rezultat
    )
    

# registracija - meni
@app.route("/registracija", methods=["GET", "POST"])
def registracija():

    sporocilo = ""

    if request.method == "POST":

        uporabnisko_ime = request.form["uporabnisko_ime"]
        geslo = request.form["geslo"]

        conn = povezava_baza()
        cur = conn.cursor()

        try:

            cur.execute("""
            INSERT INTO uporabniki
            (uporabnisko_ime, geslo)

            VALUES (?, ?)

            """,
            (uporabnisko_ime, geslo))


            conn.commit()

            sporocilo = "Registracija uspešna!"

        except Exception:

            sporocilo = "Uporabniško ime že obstaja."


        conn.close()


    return render_template(
        "registracija.html",
        sporocilo=sporocilo
    )
    

# prijava - meni
@app.route("/prijava", methods=["GET", "POST"])
def prijava():

    sporocilo = ""

    if request.method == "POST":

        uporabnisko_ime = request.form["uporabnisko_ime"]
        geslo = request.form["geslo"]


        conn = povezava_baza()
        cur = conn.cursor()


        cur.execute("""
        SELECT id
        FROM uporabniki
        WHERE uporabnisko_ime = ?
        AND geslo = ?

        """,
        (uporabnisko_ime, geslo))


        uporabnik = cur.fetchone()


        conn.close()


        if uporabnik:

            session["uporabnik_id"] = uporabnik["id"]
            session["uporabnisko_ime"] = uporabnisko_ime

            return redirect("/forum")


        else:

            sporocilo = "Napačno uporabniško ime ali geslo."


    return render_template(
        "prijava.html",
        sporocilo=sporocilo
    )
    
 
# forum - meni   
@app.route("/forum", methods=["GET", "POST"])
def forum():

    if "uporabnik_id" not in session:
        return redirect("/prijava")


    sporocilo = ""


    if request.method == "POST":

        komentar = request.form["vsebina"].strip()


        conn = povezava_baza()
        cur = conn.cursor()


        cur.execute("""
        INSERT INTO komentarji
        (uporabnik_id, vsebina, datum)

        VALUES (?, ?, datetime('now'))

        """,
        (
            session["uporabnik_id"],
            komentar
        ))


        conn.commit()
        conn.close()


        sporocilo = "Komentar dodan."


    komentarji = pridobi_komentarje()


    return render_template(
        "forum.html",
        komentarji=komentarji,
        sporocilo=sporocilo
    )
    

# odjava - meni
@app.route("/odjava")
def odjava():

    session.clear()

    return redirect("/")
     
           
if __name__ == "__main__":
    app.run(debug=True)