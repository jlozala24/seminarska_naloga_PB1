# seminarska_naloga_PB1
Seminarska naloga pri Podatkovnih bazah 1: Moški smučarski skoki v Planici
Namen projekta je ustvariti spetno stran v kateri lahko najdeš različne podatke o razultatih/državah/tekmovalcih... o smučarskih skokih v Planici za zadnijh 10 let (2015 - 2025)
Seminarska naloga vsebuje tabele o tekmovalcih, rezultatih, uporabnikih in komentarjih.


# Navodila za zagon in uporabo:
- datoteka init_db.py iz csv datotek s podatki ustvari 4 baze: rezultati, tekmovalci, uporabniki in komentarji
- vsak rezultat in tekmovalec imata svoj id preko katerega so podatki povezani
- prav tako sta tabeli komentarji in uporabniki povezani preko uporabnik_id
- pogosto pride do tega, da je pri zagonu na novem računalniku potrebno ponovno ustvariti bazo preko init_db.py datoteke
- mapa static ima css ter vse slike, ki so na spletni strani uporabljene
- templates ima html za vsako posamezno stran
- apliakcija.py je glavni spletni vmesnik. Po zagonu datoteke se v terminalu izpiše naslov/link spletne strani (http://127.0.0.1:5000). Ta link vodi do začetne spletne strani
- Na začetku ima vsak uporabnik na voljo razdelka registracija in prijava. Najprej se registriraš s poljubnim uporabniškim imenom in geslom, ki se shranita v tabelo uporabniki. Po registraciji se prijaviš, nato pa se ti odpre razdelek forum, kamor lahko zapišeš komentar, ki se shrani v tabelo komentarji (tudi čas objave).

