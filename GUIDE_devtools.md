# Prise en main des DevTools du navigateur

> Les DevTools sont l'outil intégré à votre navigateur (Chrome, Firefox, Edge...) pour observer le trafic web. Pas d'installation, pas de configuration réseau : on les ouvre, et on regarde ce que le navigateur envoie et reçoit réellement.

---

## 1. Ouvrir les DevTools

`F12`, ou clic droit n'importe où sur la page → **Inspecter**. Un panneau s'ouvre (en bas ou sur le côté). Allez directement sur l'onglet **Network**.

---

## 2. L'onglet Network

Le lab lancé (`python app.py`), DevTools ouverts sur l'onglet **Network**, visitez `http://127.0.0.1:5000/`.
La liste des requêtes apparaît au fur et à mesure que la page se charge. **Vous voyez passer votre trafic.** C'est gagné.

> Cochez **Preserve log** (icône ou case en haut de l'onglet) pour garder l'historique des requêtes même quand vous naviguez d'une page à l'autre — sinon la liste se vide à chaque rechargement.

Cliquez sur une requête dans la liste : un panneau de détail s'ouvre avec plusieurs sous-onglets :

- **Headers** : l'URL, la méthode, les en-têtes envoyés par le navigateur (*Request Headers*) et ceux renvoyés par le serveur (*Response Headers*).
- **Payload** / **Request** : ce que le navigateur a envoyé (par exemple les champs d'un formulaire).
- **Response** / **Preview** : ce que le serveur a **réellement renvoyé**, en texte brut. *C'est ici qu'on lit ce que la page ne montre pas.*
- **Cookies** : les cookies échangés sur cette requête précise.

---

## 3. L'onglet Application (cookies)

Pour voir et **modifier** les cookies posés par le site : onglet **Application** (Chrome/Edge) ou **Storage** (Firefox) → **Cookies** → `http://127.0.0.1:5000`.

Double-cliquez sur la valeur d'un cookie pour l'éditer directement, validez avec `Entrée`, puis rechargez la page : le nouveau cookie est envoyé.

---

## 4. Rejouer / modifier une requête

Les DevTools n'ont pas d'outil "Repeater" dédié, mais deux méthodes couvrent le même besoin :

- **Copier en fetch** : clic droit sur une requête dans l'onglet Network → **Copy → Copy as fetch**. Collez le résultat dans l'onglet **Console** des DevTools, modifiez les valeurs qui vous intéressent (URL, body, headers) directement dans le texte, puis validez avec `Entrée` : la requête part avec vos modifications et la réponse s'affiche dans la console.
- **Copier en curl** : même clic droit → **Copy → Copy as cURL**. Collez la commande dans un terminal, modifiez-la (par exemple changer un numéro de facture ou un mot de passe), et exécutez-la.

Idéal pour l'IDOR (changer un numéro dans l'URL) ou pour vérifier une hypothèse rapidement sans tout refaire à la souris.

---

## Le réflexe à prendre aujourd'hui

**Toujours lire la réponse brute (onglet Response), pas seulement la page affichée.**
Le navigateur vous montre ce que le développeur a *décidé* de montrer. L'onglet Network vous montre ce que le serveur a *réellement envoyé*. La différence entre les deux, c'est souvent là que se cache la faille.
