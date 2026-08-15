from flask import Flask, render_template, request, session, redirect
import model


app = Flask(__name__)

app.secret_key = "planica skrivnost"


# -------------------------------------------------
# DOMAČA STRAN
# -------------------------------------------------

@app.route("/")
def domov():
    return render_template("index.html")


# -------------------------------------------------
# ISKANJE REZULTATA
# -------------------------------------------------

@app.route("/iskanje", methods=["GET", "POST"])
def iskanje():

    rezultat = None
    iskano = False

    moznosti = model.moznosti_izbire()

    leto = request.values.get("leto", "")
    tekmovalec_id = request.values.get(
        "tekmovalec_id",
        type=int
    )

    if leto and tekmovalec_id is not None:

        iskano = True

        rezultat = model.rezultat_tekme(
            leto,
            tekmovalec_id
        )

    return render_template(
        "iskanje.html",
        rezultat=rezultat,
        iskano=iskano,
        izbrano_leto=leto,
        izbrani_tekmovalec_id=tekmovalec_id,
        **moznosti
    )


# -------------------------------------------------
# LESTVICA
# -------------------------------------------------

@app.route("/lestvica", methods=["GET", "POST"])
def stran_lestvica():

    rezultati = None

    moznosti = model.moznosti_izbire()

    leto = request.values.get("leto")

    if leto:
        rezultati = model.lestvica(leto)

    return render_template(
        "lestvica.html",
        rezultati=rezultati,
        leto=leto,
        **moznosti
    )


# -------------------------------------------------
# PROFIL TEKMOVALCA
# -------------------------------------------------

@app.route("/profil", methods=["GET", "POST"])
def profil():

    rezultati = None
    sporocilo = ""

    moznosti = model.moznosti_izbire()

    tekmovalec_id = request.values.get(
        "tekmovalec_id",
        type=int
    )

    ime = request.values.get(
        "ime",
        ""
    ).strip()

    priimek = request.values.get(
        "priimek",
        ""
    ).strip()

    if tekmovalec_id is not None:

        rezultati = model.profil_tekmovalca(
            tekmovalec_id=tekmovalec_id
        )

    elif ime and priimek:

        rezultati = model.profil_tekmovalca(
            ime=ime,
            priimek=priimek
        )

    if (tekmovalec_id is not None
            or (ime and priimek)):

        if not rezultati:

            sporocilo = (
                "Izbrani tekmovalec ni nastopal "
                "v Planici med letoma 2015 in 2025."
            )

    return render_template(
        "profil.html",
        rezultati=rezultati,
        sporocilo=sporocilo,
        izbrani_tekmovalec_id=tekmovalec_id,
        **moznosti
    )


# -------------------------------------------------
# STATISTIKA
# -------------------------------------------------

@app.route("/statistika", methods=["GET", "POST"])
def stran_statistika():

    rezultat = None
    graf = None
    sporocilo = ""

    moznosti = model.moznosti_izbire()

    tekmovalec_id = request.values.get(
        "tekmovalec_id",
        type=int
    )

    if tekmovalec_id is not None:

        tekmovalec = model.tekmovalec_po_id(
            tekmovalec_id
        )

        if tekmovalec:

            rezultat = model.statistika(
                tekmovalec["ime"],
                tekmovalec["priimek"]
            )

            graf = model.podatki_graf(
                tekmovalec["ime"],
                tekmovalec["priimek"]
            )

            if rezultat[0] == 0:

                sporocilo = (
                    "Izbrani tekmovalec ni nastopal "
                    "v Planici med letoma 2015 in 2025."
                )

    return render_template(
        "statistika.html",
        rezultat=rezultat,
        sporocilo=sporocilo,
        graf=graf,
        izbrani_tekmovalec_id=tekmovalec_id,
        **moznosti
    )

    # -------------------------------------------------
# DRŽAVA
# -------------------------------------------------


@app.route("/drzava", methods=["GET", "POST"])
def drzava():

    tekmovalci = None

    moznosti = model.moznosti_izbire()

    izbrana_drzava = request.values.get(
        "drzava",
        ""
    ).strip()

    if izbrana_drzava:

        tekmovalci = model.tekmovalci_drzava(
            izbrana_drzava
        )

    return render_template(
        "drzava.html",
        tekmovalci=tekmovalci,
        izbrana_drzava=izbrana_drzava,
        **moznosti
    )


# -------------------------------------------------
# ZMAGOVALCI
# -------------------------------------------------

@app.route("/zmagovalci")
def stran_zmagovalci():

    rezultat = model.zmagovalci()

    return render_template(
        "zmagovalci.html",
        rezultat=rezultat
    )


# -------------------------------------------------
# REGISTRACIJA
# -------------------------------------------------

@app.route("/registracija", methods=["GET", "POST"])
def registracija():

    sporocilo = ""

    if request.method == "POST":

        uporabnisko_ime = request.form[
            "uporabnisko_ime"
        ]

        geslo = request.form[
            "geslo"
        ]

        uspeh = model.dodaj_uporabnika(
            uporabnisko_ime,
            geslo
        )

        if uspeh:

            sporocilo = (
                "Registracija uspešna!"
            )

        else:

            sporocilo = (
                "Uporabniško ime že obstaja."
            )

    return render_template(
        "registracija.html",
        sporocilo=sporocilo
    )


# -------------------------------------------------
# PRIJAVA
# -------------------------------------------------

@app.route("/prijava", methods=["GET", "POST"])
def prijava():

    sporocilo = ""

    if request.method == "POST":

        uporabnisko_ime = request.form[
            "uporabnisko_ime"
        ]

        geslo = request.form[
            "geslo"
        ]

        uporabnik = model.preveri_uporabnika(
            uporabnisko_ime,
            geslo
        )

        if uporabnik:

            session["uporabnik_id"] = (
                uporabnik["id"]
            )

            session["uporabnisko_ime"] = (
                uporabnik["uporabnisko_ime"]
            )

            return redirect("/forum")

        else:

            sporocilo = (
                "Napačno uporabniško ime "
                "ali geslo."
            )

    return render_template(
        "prijava.html",
        sporocilo=sporocilo
    )


# -------------------------------------------------
# FORUM / KOMENTARJI
# -------------------------------------------------

@app.route("/forum", methods=["GET", "POST"])
def forum():

    if "uporabnik_id" not in session:

        return redirect("/prijava")

    sporocilo = ""

    if request.method == "POST":

        komentar = request.form[
            "vsebina"
        ].strip()

        if komentar:

            model.dodaj_komentar(
                session["uporabnik_id"],
                komentar
            )

            sporocilo = (
                "Komentar dodan."
            )

    komentarji = model.pridobi_komentarje()

    return render_template(
        "forum.html",
        komentarji=komentarji,
        sporocilo=sporocilo
    )


# -------------------------------------------------
# ODJAVA
# -------------------------------------------------

@app.route("/odjava")
def odjava():

    session.clear()

    return redirect("/")


# -------------------------------------------------
# ZAGON APLIKACIJE
# -------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)
