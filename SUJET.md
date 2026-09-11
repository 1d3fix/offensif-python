# Lab Meridian — Sujet

## Contexte

L'application `Lab Meridian` contient dix failles de sécurité distinctes, réparties sur plusieurs catégories du Top 10 OWASP. L'objectif de cet exercice est d'identifier chaque faille, d'en extraire le flag associé, et de proposer un correctif.

**Adresse du lab** : `http://127.0.0.1:5000`, après exécution de `python app.py` sur votre machine.

**Format des flags** : `MERIDIAN{...}`.

**Outils autorisés** : les DevTools du navigateur (onglet Network — voir `GUIDE_devtools.md`), `curl`, et `bruteforce.py`.

**Cadre légal** : les techniques mises en œuvre dans cet exercice sont illégales sur tout système pour lequel vous ne disposez pas d'une autorisation écrite. Ce lab est fourni à cette seule fin d'entraînement.

---

## Méthode attendue

Avant toute tentative d'exploitation, procéder à une phase de reconnaissance :

1. Examiner le code source de la page d'accueil (`curl http://127.0.0.1:5000/` ou affichage du code source dans le navigateur).
2. Relever les commentaires HTML.
3. Identifier et lire intégralement le fichier JavaScript chargé par la page, commentaires compris.

Toute anomalie relevée (route inhabituelle, clé, identifiant, commentaire de type TODO) constitue un point d'entrée potentiel pour les exercices suivants.

Certaines failles de ce sujet ne sont pas signalées par la reconnaissance textuelle : elles correspondent à des chemins standards qu'un attaquant teste systématiquement (dossiers de sauvegarde, dossiers de contrôle de version, fichiers de configuration d'environnement). Leur découverte peut nécessiter un outil de fuzzing de chemins (`ffuf`, `gobuster`, `dirb`) associé à une wordlist de noms courants.

---

## Exercice 1 — Configuration de débogage exposée

**Catégorie** : Security Misconfiguration (OWASP A05).

**Consigne** : identifier une route exposant la configuration interne de l'application, normalement réservée à un usage de développement.

<details>
<summary>Indice 1</summary>

La reconnaissance initiale (commentaires HTML, JavaScript) fait référence à cette route.
</details>

<details>
<summary>Indice 2</summary>

Le nom de la route correspond à un terme générique de débogage.
</details>

**Flag attendu** : `MERIDIAN{...}`

**Question** : quelles informations cette route expose-t-elle, et en quoi sont-elles réutilisables pour les exercices suivants ?

---

## Exercice 2 — Fuite de clé d'API et authentification faible

**Catégorie** : Identification and Authentication Failures (OWASP A07).

**Consigne A** : le fichier JavaScript contient une clé d'API en clair. L'utiliser pour interroger l'API des factures et obtenir la liste des numéros de facture existants.

<details>
<summary>Indice</summary>

La clé est stockée dans une constante du fichier JavaScript. L'API est interrogée via un paramètre d'URL. Comparer le comportement de l'API avec et sans ce paramètre.
</details>

**Consigne B** : le compte `admin` de la page `/login` utilise un mot de passe faible ; le serveur n'impose aucune limitation du nombre de tentatives. Déterminer ce mot de passe.

<details>
<summary>Indice</summary>

Utiliser `bruteforce.py` contre `http://127.0.0.1:5000/login` avec la wordlist fournie. Le serveur répond 401 en cas d'échec, 200 en cas de succès.

Optionnel : pour tester avec une liste de mots de passe plus représentative, télécharger [`darkc0de.txt`](https://github.com/danielmiessler/SecLists/blob/master/Passwords/darkc0de.txt) (SecLists, ~1,47M entrées — `rockyou.txt` n'étant pas préinstallé sur macOS) et l'enregistrer à côté de `bruteforce.py` :
```
python3 bruteforce.py http://127.0.0.1:5000/login admin darkc0de.txt
```
Le script testant les mots un par un, l'exécution peut être longue avec une liste de cette taille.
</details>

**Flag attendu** : `MERIDIAN{...}`

**Question** : deux défauts distincts sont combinés ici (le mot de passe et l'absence de limitation des tentatives). Lequel des deux corrigeriez-vous en priorité, et pourquoi ?

---

## Exercice 3 — Contrôle d'accès défaillant sur une ressource (IDOR)

**Catégorie** : Broken Access Control (OWASP A01) — Insecure Direct Object Reference.

**Consigne** : la facture de l'utilisateur est accessible à une adresse du type `/facture/42`. Aucune vérification n'est effectuée sur le droit d'accès à un numéro donné. Identifier la facture non autorisée correspondant au flag.

<details>
<summary>Indice</summary>

Modifier le numéro dans l'URL. La liste des numéros obtenue à l'exercice 2 contient une valeur qui ne suit pas la séquence des autres.
</details>

**Flag attendu** : `MERIDIAN{...}`

**Question** : quelle vérification est absente côté serveur, et à quel niveau du traitement de la requête devrait-elle être ajoutée ?

---

## Exercice 4 — Exposition de données via une API verbeuse

**Catégorie** : exposition de données sensibles / énumération de comptes.

**Consigne** : la page `/register` affiche uniquement « nom déjà pris » lors d'une tentative de création du compte `admin`. Déterminer les informations réellement renvoyées par le serveur.

<details>
<summary>Indice 1</summary>

Le formulaire appelle une API interne. Le JavaScript n'affiche qu'un seul champ de la réponse.
</details>

<details>
<summary>Indice 2</summary>

Dans les DevTools, onglet Network, identifier la requête envoyée par le formulaire et consulter l'intégralité de son onglet Response.
</details>

**Flag attendu** : `MERIDIAN{...}`

**Question** : quelle est la place correcte de la logique de sécurité — côté client ou côté serveur ? Que devrait renvoyer une API correctement conçue dans ce cas ?

Un second endpoint présente un défaut similaire, portant sur les profils utilisateurs.

---

## Exercice 5 — Élévation de privilèges par falsification de cookie

**Catégorie** : Broken Access Control (OWASP A01).

**Consigne** : la route `/admin/console` est réservée aux comptes administrateurs. Y accéder sans authentification administrateur.

<details>
<summary>Indice 1</summary>

Se connecter avec le compte `demo` (identifiants dans le README). Examiner le cookie déposé par le serveur (DevTools → Application → Cookies, ou en-tête `Set-Cookie`).
</details>

<details>
<summary>Indice 2</summary>

Ce cookie n'est ni signé ni chiffré. Modifier sa valeur directement depuis l'onglet Application des DevTools, puis accéder de nouveau à `/admin/console`.
</details>

**Flag attendu** : `MERIDIAN{...}`

**Question** : quelle hypothèse de confiance, côté serveur, est ici incorrecte ? Où l'information de rôle devrait-elle être stockée ?

---

## Exercice 6 — Listing de répertoire non désactivé

**Catégorie** : Security Misconfiguration (OWASP A05).

**Consigne** : un répertoire du serveur est accessible avec listing complet des fichiers. Ni la page d'accueil ni le JavaScript n'en font mention.

<details>
<summary>Indice</summary>

Utiliser un outil de fuzzing de chemins avec une wordlist de noms de répertoires courants (sauvegarde, export, archive). Une recherche manuelle est également possible.
</details>

**Flag attendu** : `MERIDIAN{...}`

**Question** : un des fichiers du répertoire recoupe une faille déjà identifiée dans un exercice précédent — lequel, et pourquoi ? Quel réglage serveur permet d'empêcher ce type de listing ?

---

## Exercice 7 — Exposition d'un dépôt de contrôle de version

**Catégorie** : Security Misconfiguration — exposition de métadonnées de VCS.

**Consigne** : un dossier de métadonnées d'un système de contrôle de version a été déployé avec l'application. Reconstruire l'historique du dépôt et identifier un secret présent dans un commit antérieur.

<details>
<summary>Indice 1</summary>

Tester la présence d'un dossier standard, commençant par un point. Un des fichiers qu'il contient n'est pas compressé et peut être lu directement.
</details>

<details>
<summary>Indice 2</summary>

Outil de reconstruction recommandé : **git-dumper**.
```
pip install git-dumper
git-dumper http://127.0.0.1:5000/.git/ ./dump
cd dump
git log --oneline
```
Examiner l'historique complet d'un fichier, pas seulement sa version actuelle.
</details>

**Flag attendu** : `MERIDIAN{...}`

**Question** : la suppression d'un secret dans un commit ultérieur suffit-elle à le retirer de l'historique du dépôt ? Quelle action corrective est réellement nécessaire ?

---

## Exercice 8 — Exposition d'un fichier de configuration d'environnement

**Catégorie** : Security Misconfiguration (OWASP A05).

**Consigne** : un fichier de configuration contenant des variables d'environnement est accessible publiquement.

<details>
<summary>Indice</summary>

Nom de fichier standard pour ce type de configuration (clés d'API, identifiants de base de données), débutant par un point.
</details>

**Flag attendu** : `MERIDIAN{...}`

**Question** : le fichier contient plusieurs clés au format de services cloud réels (toutes invalides ici). Quelle est la première action à mener en cas de découverte d'une fuite de ce type, avant même la correction de la cause ?

---

## Exercice 9 — Fingerprinting de la stack technique

**Catégorie** : exposition d'information / reconnaissance d'infrastructure.

**Consigne** : identifier les informations sur la stack technique exposées par le serveur, au-delà de ce qui est strictement nécessaire.

<details>
<summary>Indice 1</summary>

Examiner les en-têtes de réponse HTTP de n'importe quelle page (DevTools → Network → Headers → Response Headers).
</details>

<details>
<summary>Indice 2</summary>

Un endpoint dédié renvoie ces informations de façon détaillée, au format JSON.
</details>

**Flag attendu** : `MERIDIAN{...}`

**Question** : à quel usage légitime répondent un en-tête `Server` ou un endpoint de version ? Comment concilier cet usage avec une restriction d'accès appropriée ?

---

## Exercice 10 — Fuite d'information par métadonnées de document

**Catégorie** : fuite d'information via métadonnées (OSINT).

**Consigne** : la facture accessible via `/facture/42` peut être téléchargée au format PDF. Examiner les métadonnées du document généré, indépendamment de son contenu visible.

<details>
<summary>Indice 1</summary>

Outils d'extraction de métadonnées PDF : `exiftool`, `pdfinfo`, ou `strings` combiné à un `grep` sur le préfixe des flags.
</details>

<details>
<summary>Indice 2</summary>

Un champ précis, rarement renseigné dans un document standard, contient ici une référence interne ajoutée par le moteur de génération.
</details>

**Flag attendu** : `MERIDIAN{...}`

**Question** : l'accès au document est légitime. Où se situe alors le problème ? Ce type de fuite (métadonnées Word, PDF, EXIF) a-t-il déjà, à votre connaissance, permis d'identifier l'auteur d'un document destiné à rester anonyme ?

---

## Rendu attendu

Pour chaque exercice :
1. le flag obtenu ;
2. une description de la méthode d'exploitation (deux phrases maximum) ;
3. une proposition de correction (une phrase).

Le point 3 est déterminant dans l'évaluation. L'identification de la faille relève du travail de l'attaquant ; sa correction relève du vôtre.

---

## Pour aller plus loin (facultatif)

- Automatiser l'exercice 3 : un script appelant `/facture/N` pour `N` de 1 à 200, avec comparaison de la taille des réponses, permet d'identifier l'ensemble des factures existantes.
- Analyser le fichier `acces.log` généré localement : identifier, dans ce journal, les traces laissées par les exercices 2 (bruteforce) et 3 (IDOR), à l'aide du script `analyse.py` d'un TP précédent.
