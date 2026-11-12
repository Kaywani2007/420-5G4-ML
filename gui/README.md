# Interface graphique de la bibliothèque personnelle

Application Python avec `customtkinter` qui reproduit les fonctionnalités du
gestionnaire de bibliothèque C++ de `agent/`.

## Fonctionnalités

- affichage de tous les livres et de tous les utilisateurs ;
- recherche insensible à la casse et aux accents par titre ou par auteur ;
- tri alphabétique par titre ou par nom complet d'auteur ;
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

## Recherche et tri

- Le critère **Titre** ou **Auteur** est appliqué au clic sur **Rechercher** ou
  avec la touche **Entrée**.
- Si le champ de recherche est vide, tous les livres sont affichés dans l'ordre
  alphabétique du critère sélectionné.
- Le tri par titre est littéral : les articles initiaux comme « Le » ou « Les »
  ne sont pas retirés.
- Le tri par auteur utilise le nom complet tel qu'il est saisi.
- La casse et les accents sont ignorés pour le tri et la recherche.
- Le tri s'applique aussi aux résultats d'une recherche et reste combiné avec
  les filtres **Tous**, **Disponibles** et **Empruntés**.
- Changer seulement le critère ne modifie pas le tableau tant que **Rechercher**
  ou **Entrée** n'a pas été utilisé.

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

Les tests d'interface sont ignorés automatiquement si `customtkinter` ou un
affichage graphique ne sont pas disponibles. Pour les exécuter sans écran sous
Linux, utiliser `xvfb-run` avec le Python du venv.

## Organisation du code

```text
gui/
  app.py                    # point d'entrée
  bibliotheque/
    modeles.py              # Livre et Utilisateur
    stockage.py             # lecture, écriture et sauvegardes
    service.py              # règles métier de la bibliothèque
    texte.py                # normalisation recherche et tri
  ui/
    fenetre_principale.py   # fenêtre, navigation, barre d'état
    page_livres.py
    page_utilisateurs.py
    page_emprunts.py
    page_statistiques.py
    dialogues.py
    composants.py
    tri_livres.py
  tests/
    test_bibliotheque.py
    test_page_livres_ui.py
    test_tri_livres.py
```

Le répertoire `gui/.venv/` est ignoré par Git.
