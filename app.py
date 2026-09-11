"""
LAB MERIDIAN - application volontairement vulnerable (OWASP + DevTools navigateur).

A LANCER UNIQUEMENT EN LOCAL, dans un cadre pedagogique.
Contient des failles VOLONTAIRES. Aucune vraie donnee.

Failles :
  - Recon : fuites dans les commentaires HTML et JS
  - A05 Misconfiguration : route /debug active, secrets exposes
  - A07 Auth faible : mot de passe admin faible, aucun verrouillage
  - A01 IDOR : /facture/<id> sans controle d'acces
  - A01 Cookie tampering : cookie 'role' non signe (role=user -> admin)
  - API verbeuse : /api/register et /api/profil renvoient trop d'infos
  - A05 Listing de repertoire ouvert : /backups/
  - A05 Depot .git deploye par erreur : /.git/ (secret dans l'historique)
  - A05 Fichier .env expose : /.env
  - Fingerprinting : en-tetes trop precis + /api/version bavard
  - Fuite de metadonnees : /facture/<id>/pdf (PDF genere avec metadonnees internes)

Lancement (en local) :
    pip install -r requirements.txt
    python app.py
Puis : http://127.0.0.1:5000/
"""

from flask import (Flask, request, render_template, jsonify, make_response,
                    send_from_directory, Response)
from datetime import datetime
from fpdf import FPDF
import os
import sqlite3

app = Flask(__name__)

FICHIER_LOG = "acces.log"
BASE = "lab.db"
API_KEY = "dev-meridian-7f3a9c"
DOSSIER_BACKUPS = "backups"
DOSSIER_GIT_EXPOSE = "git_data"

CONTENU_ENV = """# Meridian Corp - configuration production (NE JAMAIS COMMITER)
FLASK_ENV=production
SECRET_KEY=8f3ad1c9e6b7409f9a1d9e0c6a2b7f31
DATABASE_URL=sqlite:///lab.db
AWS_ACCESS_KEY_ID=AKIAJ7ZQXMPLE2FAKE01
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
STRIPE_SECRET_KEY=sk_live-FAKE-DO-NOT-USE-0000000000000000
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T000000/B000000/FAKEwebhookEXAMPLE0000
MAIL_PASSWORD=Corr3sp0ndance!2024
INTERNAL_FLAG=MERIDIAN{dotenv_expose_en_prod}
"""

FACTURES = {
    41: {"client": "Alice Dupont", "montant": "1 240 EUR", "detail": "Prestation conseil"},
    42: {"client": "Vous (compte demo)", "montant": "90 EUR", "detail": "Abonnement mensuel"},
    43: {"client": "Bruno Martin", "montant": "310 EUR", "detail": "Support technique"},
    3:  {"client": "Sofia Meridian (PDG)", "montant": "48 000 EUR",
         "detail": "Prime annuelle - CONFIDENTIEL - MERIDIAN{idor_facture_du_ceo}"},
}


def init_base():
    con = sqlite3.connect(BASE)
    con.execute("""CREATE TABLE IF NOT EXISTS utilisateurs (
        username TEXT PRIMARY KEY, password TEXT, role TEXT, email TEXT, note TEXT)""")
    con.execute("INSERT OR IGNORE INTO utilisateurs VALUES (?,?,?,?,?)",
                ("admin", "letmein", "admin", "admin@meridian.corp",
                 "compte principal - MERIDIAN{lis_la_vraie_reponse}"))
    con.execute("INSERT OR IGNORE INTO utilisateurs VALUES (?,?,?,?,?)",
                ("demo", "demo", "user", "demo@meridian.corp", "compte de demonstration"))
    con.commit()
    con.close()


def get_user(username):
    con = sqlite3.connect(BASE)
    cur = con.execute("SELECT username,password,role,email,note FROM utilisateurs WHERE username=?", (username,))
    ligne = cur.fetchone()
    con.close()
    if ligne is None:
        return None
    return {"username": ligne[0], "password": ligne[1], "role": ligne[2],
            "email": ligne[3], "note": ligne[4]}


@app.after_request
def journaliser(reponse):
    h = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(FICHIER_LOG, "a", encoding="utf-8") as f:
        f.write(h + ";" + request.remote_addr + ";" + request.method + ";" +
                request.path + ";" + str(reponse.status_code) + "\n")
    return reponse


# --- Faille : en-tete applicatif trop precis sur la stack technique ---
# (le serveur de dev Werkzeug ajoute deja tout seul son propre en-tete
# "Server" avec les vraies versions installees : inutile de le forcer,
# ca produirait un doublon incoherent. X-Powered-By, lui, n'est pas
# touche par Werkzeug : on peut le fixer librement.)
@app.after_request
def empreinte_serveur(reponse):
    reponse.headers["X-Powered-By"] = "Meridian-Portal/1.4.2"
    return reponse


@app.route("/")
def accueil():
    return render_template("index.html")


# --- A05 : debug laisse actif ---
@app.route("/debug")
def debug():
    return jsonify({"app": "Meridian", "debug": True, "api_key": API_KEY,
                    "database": BASE, "flag": "MERIDIAN{d3bug_rest3_activ3}"})


# --- API factures : cle qui fuite dans le JS ---
@app.route("/api/factures")
def api_factures():
    if request.args.get("key", "") != API_KEY:
        return jsonify({"erreur": "cle invalide"}), 403
    return jsonify({"factures": [{"id": i, "client": FACTURES[i]["client"]} for i in FACTURES]})


# --- A01 IDOR ---
@app.route("/facture/<int:numero>")
def facture(numero):
    return render_template("facture.html", numero=numero, facture=FACTURES.get(numero))


def generer_facture_pdf(numero, donnees):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 14, "Meridian Corp", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Facture n{numero}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.cell(0, 8, f"Client : {donnees['client']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Montant TTC : {donnees['montant']}", new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(0, 8, f"Objet : {donnees['detail']}")

    # Faille : metadonnees internes laissees dans le PDF genere.
    pdf.set_title(f"Facture Meridian n{numero}")
    pdf.set_author("Service Facturation Meridian")
    pdf.set_creator("Meridian PDF Engine v2.1 - build agent pdf-worker-03")
    pdf.set_subject(
        "Document genere automatiquement - usage interne uniquement - "
        "ref moteur MERIDIAN{metadata_pdf_qui_parle} - ne pas diffuser hors service"
    )
    pdf.set_keywords("facture,meridian,interne,confidentiel")

    return bytes(pdf.output())


# --- Faille : le PDF genere embarque des metadonnees internes (OSINT) ---
@app.route("/facture/<int:numero>/pdf")
def facture_pdf(numero):
    donnees = FACTURES.get(numero)
    if not donnees:
        return jsonify({"erreur": "facture introuvable"}), 404
    contenu = generer_facture_pdf(numero, donnees)
    return Response(contenu, mimetype="application/pdf", headers={
        "Content-Disposition": f"inline; filename=facture_{numero}.pdf",
    })


# --- A07 : login. Pose un cookie 'role' NON signe (falsifiable) ---
@app.route("/login", methods=["GET", "POST"])
def login():
    message = None
    statut = 200
    flag = None
    role_cookie = None
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "").strip()
        user = get_user(u)
        if user and user["password"] == p:
            message = "Connexion reussie."
            role_cookie = user["role"]
            if user["role"] == "admin":
                flag = "MERIDIAN{mdp_faible_pas_de_verrou}"
        else:
            message = "Identifiants incorrects."
            statut = 401
    reponse = make_response(render_template("login.html", message=message, flag=flag), statut)
    if role_cookie:
        # Faille : le role est stocke en clair cote client, sans signature.
        reponse.set_cookie("role", role_cookie)
    return reponse


# --- A01 : espace admin protege UNIQUEMENT par le cookie 'role' ---
@app.route("/admin/console")
def admin_console():
    role = request.cookies.get("role", "invite")
    if role != "admin":
        return render_template("refus.html", role=role), 403
    return render_template("console.html", flag="MERIDIAN{cookie_role_admin}")


# --- API verbeuse : le front n'affiche qu'un message, l'API en dit trop ---
@app.route("/api/register", methods=["POST"])
def api_register():
    donnees = request.json if request.is_json else request.form
    u = (donnees.get("username") or "").strip()
    email = (donnees.get("email") or "").strip()
    mdp = (donnees.get("password") or "").strip()

    if not u or not mdp:
        return jsonify({"message": "Identifiant et mot de passe requis."}), 400

    existant = get_user(u)
    if existant:
        # Le front affichera juste "nom deja pris". Mais la reponse, elle,
        # divulgue tout le profil du compte existant (enumeration + fuite).
        return jsonify({
            "message": "Ce nom d'utilisateur est deja pris.",
            "compte_existant": {
                "username": existant["username"],
                "email": existant["email"],
                "role": existant["role"],
                "note_interne": existant["note"],
            }
        }), 409

    con = sqlite3.connect(BASE)
    con.execute("INSERT INTO utilisateurs VALUES (?,?,?,?,?)",
                (u, mdp, "user", email, "compte cree via /register"))
    con.commit()
    con.close()
    return jsonify({"message": "Compte cree."}), 201


# --- API verbeuse (bonus) : profil bien trop detaille ---
@app.route("/api/profil/<username>")
def api_profil(username):
    user = get_user(username)
    if not user:
        return jsonify({"erreur": "inconnu"}), 404
    return jsonify(user)   # renvoie meme le mot de passe : jamais faire ca


@app.route("/register")
def register_page():
    return render_template("register.html")


# --- A05 : listing de repertoire ouvert (dossier de sauvegardes oublie) ---
@app.route("/backups/")
def backups_index():
    fichiers = []
    for nom in sorted(os.listdir(DOSSIER_BACKUPS)):
        chemin = os.path.join(DOSSIER_BACKUPS, nom)
        fichiers.append({
            "nom": nom,
            "taille": f"{os.path.getsize(chemin)}",
            "modifie": datetime.fromtimestamp(os.path.getmtime(chemin)).strftime("%d-%b-%Y %H:%M"),
        })
    return render_template("index_of.html", chemin="/backups/", fichiers=fichiers)


@app.route("/backups/<path:nom>")
def backups_fichier(nom):
    return send_from_directory(DOSSIER_BACKUPS, nom)


# --- A05 : depot .git deploye par erreur avec le reste du site ---
# Le secret a ete "retire" dans un commit ulterieur : il ne reste QUE
# dans l'historique git, jamais dans le fichier courant. On sert ici
# les fichiers internes de .git tels quels, comme le ferait un serveur
# web mal configure qui n'exclut pas les dossiers caches.
@app.route("/.git/<path:nom>")
def git_expose(nom):
    return send_from_directory(DOSSIER_GIT_EXPOSE, nom)


# --- A05 : fichier .env deploye avec le reste du site ---
@app.route("/.env")
def dotenv_expose():
    return Response(CONTENU_ENV, mimetype="text/plain")


# --- Fingerprinting : endpoint de sante bien trop bavard ---
@app.route("/api/version")
def api_version():
    return jsonify({
        "app": "Meridian Portal",
        "version": "1.4.2",
        "build": "2024.01.08-prod",
        "stack": {
            "framework": "Flask 2.3.1",
            "python": "3.11.4",
            "serveur": "Werkzeug 3.0.1",
            "os": "Ubuntu 22.04 LTS",
        },
        "note_interne": "endpoint de sante technique - devrait etre derriere l'authentification",
        "flag": "MERIDIAN{stack_trop_bavarde}",
    })


if __name__ == "__main__":
    init_base()
    print("Lab Meridian sur http://127.0.0.1:5000/")
    print("Arret : Ctrl + C")
    app.run(host="127.0.0.1", port=5000, threaded=True, debug=False)
