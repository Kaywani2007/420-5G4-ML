# AGENTS.md

## Repository shape
- Three independent assignment parts: `apprentissage/` (Pokémon win-rate regression), `analyse_image/` (Fashion-MNIST CNN), `agent/` (C++17 library manager).
- No root build/test/lint/CI orchestrator; each part is run separately.
- There are no automated tests, linters, or formatters.

## C++ app (`agent/`)
- Build:
  ```bash
  cd agent
  mkdir -p build && cd build
  cmake ..
  make
  ```
- Run from `agent/build`: `./bibliotheque -d ../data`
- `CMakeLists.txt` uses `file(GLOB SOURCES "*.cpp")`; rerun `cmake ..` after adding/removing `.cpp` files.
- Without `-d`, data file paths are empty, so saves fail and state is memory-only.
- Using `-d ../data` reads and overwrites the tracked fixtures `agent/data/books.txt` and `users.txt` (including on exit). Copy them to a temp directory for disposable testing.
- Storage formats:
  - `books.txt`: `title|author|isbn|available(1/0)|borrowerId`
  - `users.txt`: `name|userId|comma-separated ISBNs`
- Ignore `.vscode/settings.json`; it hardcodes a stale Windows path. Build from `agent/CMakeLists.txt`.
- `agent/build/` is gitignored; do not edit generated files there.

## Python notebooks
- Run Jupyter from each notebook's own directory; paths are relative to the notebook:
  - `apprentissage/` uses `../data/` and `../modele/`
  - `analyse_image/` uses `datas/`, `modele/`, and `images/`
- Pipeline: `apprentissage/partie1_2.ipynb` writes `data/dataset.csv`; `partie3_entrainement.ipynb` writes `modele/modele_pokemon.mod`; `partie3_predictions.ipynb` loads both.
- `data/dataset.csv` is tab-separated with an unnamed leading index column; preserve that when editing.
- No requirements or `pyproject.toml`. Imports require pandas, numpy, matplotlib, seaborn, scikit-learn, joblib, TensorFlow/Keras, and Pillow.
- `.venv/` is a Windows-only venv (`Scripts/`, Windows paths in `pyvenv.cfg`) and is gitignored; do not use it on Linux.
- `analyse_image/datas/*.csv` and `*.idx*` are gitignored and untracked, so they may be missing on a fresh clone.
- `analyse_image/classification.ipynb` is expensive: CNN training up to 50 epochs and forces CPU.

## Conventions
- C++ is built as C++17 with `-Wall -Wextra -Wpedantic`.
- Keep user-facing C++ output and notebook labels in French.
