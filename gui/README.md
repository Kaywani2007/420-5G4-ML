# Interface graphique de la bibliothèque personnelle

Application Python avec `customtkinter` qui reproduit les fonctionnalités du
gestionnaire de bibliothèque C++ de `agent/`.

## Fonctionnalités

- affichage de tous les livres et de tous les utilisateurs ;
- recherche insensible à la casse par titre ou par auteur ;
- filtres **Tous**, **Disponibles** et **Empruntés** ;
- ajout d'un livre avec contrôle des doublons d'ISBN ;
- suppression d'un livre, bloquée s'il est actuellement emprunté ;
- ajout d'un utilisateur avec contrôle des doublons d'ID ;
- emprunt d'un livre disponible par un utilisateur ;
- retour d'un livre emprunté ;
- statistiques de la bibliothèque ;
- sauvegarde automatique après chaque modification ;
- sauvegarde manuelle et création de fichiers `.backup`.

L'interface est entièrement en français.

## Données

Les fichiers utilisés sont ceux du projet C++ :

- `../agent/data/books.txt`
- `../agent/data/users.txt`

Leur format est conservé sans modification :

- livres : `titre|auteur|isbn|disponible(1/0)|idEmprunteur`
- utilisateurs : `nom|id|isbn1,isbn2,...`

Les chemins sont résolus à partir de l'emplacement du code Python, ce qui permet
de lancer l'application depuis `gui/` sans dépendre du répertoire courant.

## Prérequis

- Python 3 avec `tkinter`
- Un affichage graphique disponible (serveur X11 ou session de bureau)

## Installation

```bash
cd gui
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Sous Windows :

```powershell
cd gui
py -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt
```

## Lancement

```bash
cd gui
.venv/bin/python app.py
```

Sous Windows :

```powershell
cd gui
.venv\Scripts\python app.py
```

## Tests

Les tests utilisent uniquement des fichiers temporaires et ne modifient jamais
les données réelles :

```bash
cd gui
python3 -m unittest discover -s tests -v
```

## Organisation du code

```text
gui/
  app.py                    # point d'entrée
  bibliotheque/
    modeles.py              # Livre et Utilisateur
    stockage.py             # lecture, écriture et sauvegardes
    service.py              # règles métier de la bibliothèque
  ui/
    fenetre_principale.py   # fenêtre, navigation, barre d'état
    page_livres.py
    page_utilisateurs.py
    page_emprunts.py
    page_statistiques.py
    dialogues.py
    composants.py
  tests/
    test_bibliotheque.py
```

Le répertoire `gui/.venv/` est ignoré par Git.
