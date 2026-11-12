from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Iterable, TypeVar

from .modeles import Livre, Utilisateur

T = TypeVar("T")


class ErreurStockage(Exception):
    """Erreur liée à la lecture ou à l'écriture des fichiers de données."""


def chemin_donnees_par_defaut() -> Path:
    return Path(__file__).resolve().parents[2] / "agent" / "data"


class Stockage:
    def __init__(
        self,
        chemin_livres: str | Path | None = None,
        chemin_utilisateurs: str | Path | None = None,
    ) -> None:
        dossier = chemin_donnees_par_defaut()
        self.chemin_livres = Path(chemin_livres) if chemin_livres else dossier / "books.txt"
        self.chemin_utilisateurs = (
            Path(chemin_utilisateurs) if chemin_utilisateurs else dossier / "users.txt"
        )

    @property
    def dossier(self) -> Path:
        return self.chemin_livres.parent

    def charger_livres(self) -> list[Livre]:
        return self._charger(self.chemin_livres, Livre)

    def charger_utilisateurs(self) -> list[Utilisateur]:
        return self._charger(self.chemin_utilisateurs, Utilisateur)

    def sauvegarder(
        self, livres: Iterable[Livre], utilisateurs: Iterable[Utilisateur]
    ) -> None:
        lignes_livres = [livre.to_file_line() for livre in livres]
        lignes_utilisateurs = [utilisateur.to_file_line() for utilisateur in utilisateurs]

        temporaire_livres: Path | None = None
        temporaire_utilisateurs: Path | None = None

        try:
            self.chemin_livres.parent.mkdir(parents=True, exist_ok=True)
            self.chemin_utilisateurs.parent.mkdir(parents=True, exist_ok=True)

            temporaire_livres = self._ecrire_temporaire(
                self.chemin_livres,
                lignes_livres,
                self._detecter_fin_ligne(self.chemin_livres),
            )
            temporaire_utilisateurs = self._ecrire_temporaire(
                self.chemin_utilisateurs,
                lignes_utilisateurs,
                self._detecter_fin_ligne(self.chemin_utilisateurs),
            )

            os.replace(temporaire_livres, self.chemin_livres)
            temporaire_livres = None
            os.replace(temporaire_utilisateurs, self.chemin_utilisateurs)
            temporaire_utilisateurs = None
        except OSError as exc:
            raise ErreurStockage(
                f"Impossible de sauvegarder les données : {exc}"
            ) from exc
        finally:
            for temporaire in (temporaire_livres, temporaire_utilisateurs):
                if temporaire is not None:
                    try:
                        temporaire.unlink(missing_ok=True)
                    except OSError:
                        pass

    def creer_sauvegarde(self) -> list[Path]:
        copies: list[Path] = []

        try:
            for source in (self.chemin_livres, self.chemin_utilisateurs):
                if source.exists():
                    cible = source.with_name(f"{source.name}.backup")
                    shutil.copy2(source, cible)
                    copies.append(cible)
        except OSError as exc:
            raise ErreurStockage(
                f"Impossible de créer la sauvegarde des fichiers : {exc}"
            ) from exc

        return copies

    def _charger(self, chemin: Path, fabrique: type[T]) -> list[T]:
        if not chemin.exists():
            return []

        try:
            with chemin.open("r", encoding="utf-8") as fichier:
                return [
                    fabrique.from_file_line(ligne)
                    for ligne in fichier
                    if ligne.strip()
                ]
        except (OSError, UnicodeError) as exc:
            raise ErreurStockage(f"Impossible de lire {chemin} : {exc}") from exc

    @staticmethod
    def _detecter_fin_ligne(chemin: Path) -> str:
        if not chemin.exists():
            return "\n"

        try:
            with chemin.open("rb") as fichier:
                for ligne in fichier:
                    if ligne.endswith(b"\r\n"):
                        return "\r\n"
                    if ligne.endswith(b"\n"):
                        return "\n"
        except OSError:
            return "\n"

        return "\n"

    @staticmethod
    def _ecrire_temporaire(
        chemin: Path, lignes: list[str], fin_ligne: str
    ) -> Path:
        temporaire = chemin.with_name(f"{chemin.name}.tmp")
        with temporaire.open("w", encoding="utf-8", newline="") as fichier:
            for ligne in lignes:
                fichier.write(f"{ligne}{fin_ligne}")
        return temporaire
