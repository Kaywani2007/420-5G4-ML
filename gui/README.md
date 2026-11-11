# Application de test CustomTkinter

Application graphique minimale avec une fenêtre et un label centré.

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

## Lancement

```bash
cd gui
.venv/bin/python app.py
```

Le répertoire `gui/.venv/` est ignoré par Git.
