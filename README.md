# Lab Meridian — installation

Une application web volontairement vulnérable, à faire tourner **sur votre propre machine**. Vous l'attaquerez en local.

---

## Lancer le lab

Il vous faut **Python 3** (déjà installé si vous avez suivi les TP précédents).

### 1. Récupérer le projet
```
git clone <URL_DU_DEPOT>
cd lab-meridian
```

### 2. Installer les dépendances

Windows :
```
pip install -r requirements.txt
```
macOS / Linux :
```
pip3 install -r requirements.txt
```

> Si pip refuse d'installer (message « externally managed »), créez un environnement isolé :
> ```
> python3 -m venv venv
> source venv/bin/activate      (Windows : venv\Scripts\activate)
> pip install -r requirements.txt
> ```

### 3. Démarrer
```
python app.py          (Windows)
python3 app.py         (macOS / Linux)
```

Vous verrez :
```
Lab Meridian sur http://127.0.0.1:5000/
Arret : Ctrl + C
```

### 4. Ouvrir dans le navigateur
```
http://127.0.0.1:5000/
```

Le portail Meridian s'affiche. Le lab tourne.

> ⚠️ Le terminal reste occupé pendant que le serveur tourne, c'est normal. Ouvrez un second terminal pour vos outils (curl, etc.), et faites Ctrl + C pour arrêter.

> 🍎 **Sur Mac** : si vous voyez « Address already in use » / « Port 5000 is in use », c'est presque toujours le **Récepteur AirPlay** de macOS qui occupe déjà le port 5000. Réglages Système → Général → AirDrop et Handoff → désactivez « Récepteur AirPlay ».

---

## Ce qu'il vous faut à côté

- Le sujet : `SUJET.md` (les failles à trouver).
- Le guide DevTools : `GUIDE_devtools.md` (prise en main de l'onglet Network du navigateur).

---

## Comptes de test

| Identifiant | Mot de passe | Rôle |
|---|---|---|
| demo  | demo | utilisateur |
| admin | (à vous de le trouver...) | administrateur |

---

## Repartir de zéro

Le lab crée deux fichiers en tournant : lab.db (la base) et acces.log (le journal). Pour tout réinitialiser :
```
rm lab.db acces.log        (Windows : del lab.db acces.log)
```

---

## Rappel

Ce lab est une cible d'entraînement. Les techniques apprises ici sont illégales sur un système qui n'est pas le vôtre. On les apprend pour savoir défendre.
