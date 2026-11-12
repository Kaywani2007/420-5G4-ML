from __future__ import annotations

import copy
from collections.abc import Callable
from pathlib import Path

from .modeles import Livre, Utilisateur
from .stockage import ErreurStockage, Stockage
from .texte import normaliser_texte


class ErreurBibliotheque(Exception):
    """Erreur de validation ou d'opération sur la bibliothèque."""


class Bibliotheque:
    def __init__(self, stockage: Stockage | None = None) -> None:
        self.stockage = stockage or Stockage()
        self.livres: list[Livre] = []
        self.utilisateurs: list[Utilisateur] = []

    def charger(self) -> None:
        try:
            self.livres = self.stockage.charger_livres()
            self.utilisateurs = self.stockage.charger_utilisateurs()
        except ErreurStockage as exc:
            raise ErreurBibliotheque(str(exc)) from exc

    def sauvegarder(self) -> None:
        try:
            self.stockage.sauvegarder(self.livres, self.utilisateurs)
        except ErreurStockage as exc:
            raise ErreurBibliotheque(str(exc)) from exc

    def creer_sauvegarde(self) -> list[Path]:
        try:
            return self.stockage.creer_sauvegarde()
        except ErreurStockage as exc:
            raise ErreurBibliotheque(str(exc)) from exc

    def trouver_livre(self, isbn: str) -> Livre | None:
        return next((livre for livre in self.livres if livre.isbn == isbn), None)

    def trouver_utilisateur(self, identifiant: str) -> Utilisateur | None:
        return next(
            (
                utilisateur
                for utilisateur in self.utilisateurs
                if utilisateur.identifiant == identifiant
            ),
            None,
        )

    def rechercher_par_titre(self, texte: str) -> list[Livre]:
        recherche = normaliser_texte(texte)
        if not recherche:
            return list(self.livres)
        return [
            livre
            for livre in self.livres
            if recherche in normaliser_texte(livre.titre)
        ]

    def rechercher_par_auteur(self, texte: str) -> list[Livre]:
        recherche = normaliser_texte(texte)
        if not recherche:
            return list(self.livres)
        return [
            livre
            for livre in self.livres
            if recherche in normaliser_texte(livre.auteur)
        ]

    @property
    def livres_disponibles(self) -> list[Livre]:
        return [livre for livre in self.livres if livre.disponible]

    @property
    def livres_empruntes(self) -> list[Livre]:
        return [livre for livre in self.livres if not livre.disponible]

    @property
    def total_livres(self) -> int:
        return len(self.livres)

    @property
    def total_disponibles(self) -> int:
        return len(self.livres_disponibles)

    @property
    def total_empruntes(self) -> int:
        return len(self.livres_empruntes)

    @property
    def total_utilisateurs(self) -> int:
        return len(self.utilisateurs)

    def verifier_ajout_livre(self, titre: str, auteur: str, isbn: str) -> None:
        _, _, isbn_valide = self._valider_livre(titre, auteur, isbn)
        if self.trouver_livre(isbn_valide):
            raise ErreurBibliotheque(
                f"Un livre avec l'ISBN {isbn_valide} existe déjà."
            )

    def ajouter_livre(self, titre: str, auteur: str, isbn: str) -> Livre:
        titre_valide, auteur_valide, isbn_valide = self._valider_livre(
            titre, auteur, isbn
        )
        if self.trouver_livre(isbn_valide):
            raise ErreurBibliotheque(
                f"Un livre avec l'ISBN {isbn_valide} existe déjà."
            )

        livre = Livre(titre_valide, auteur_valide, isbn_valide)
        self._executer_et_sauvegarder(lambda: self.livres.append(livre))
        return livre

    def supprimer_livre(self, isbn: str) -> None:
        livre = self.trouver_livre(isbn)
        if livre is None:
            raise ErreurBibliotheque("Livre non trouvé.")
        if not livre.disponible:
            raise ErreurBibliotheque(
                "Impossible de supprimer un livre emprunté. Retournez-le d'abord."
            )

        self._executer_et_sauvegarder(lambda: self.livres.remove(livre))

    def verifier_ajout_utilisateur(self, nom: str, identifiant: str) -> None:
        _, identifiant_valide = self._valider_utilisateur(nom, identifiant)
        if self.trouver_utilisateur(identifiant_valide):
            raise ErreurBibliotheque(
                f"Un utilisateur avec l'ID {identifiant_valide} existe déjà."
            )

    def ajouter_utilisateur(self, nom: str, identifiant: str) -> Utilisateur:
        nom_valide, identifiant_valide = self._valider_utilisateur(nom, identifiant)
        if self.trouver_utilisateur(identifiant_valide):
            raise ErreurBibliotheque(
                f"Un utilisateur avec l'ID {identifiant_valide} existe déjà."
            )

        utilisateur = Utilisateur(nom_valide, identifiant_valide)
        self._executer_et_sauvegarder(lambda: self.utilisateurs.append(utilisateur))
        return utilisateur

    def emprunter(self, isbn: str, identifiant: str) -> None:
        livre = self.trouver_livre(isbn)
        utilisateur = self.trouver_utilisateur(identifiant)

        if livre is None or utilisateur is None:
            raise ErreurBibliotheque(
                "Impossible d'emprunter le livre : vérifiez l'ISBN et l'ID utilisateur."
            )
        if not livre.disponible:
            raise ErreurBibliotheque("Ce livre est déjà emprunté.")

        def operation() -> None:
            livre.marquer_emprunte(utilisateur.identifiant)
            utilisateur.ajouter_emprunt(livre.isbn)

        self._executer_et_sauvegarder(operation)

    def retourner(self, isbn: str) -> None:
        livre = self.trouver_livre(isbn)
        if livre is None:
            raise ErreurBibliotheque("Impossible de retourner le livre : ISBN inconnu.")
        if livre.disponible:
            raise ErreurBibliotheque("Ce livre n'est pas actuellement emprunté.")

        def operation() -> None:
            for utilisateur in self.utilisateurs:
                if utilisateur.a_emprunte(isbn):
                    utilisateur.retirer_emprunt(isbn)
                    break
            livre.marquer_retourne()

        self._executer_et_sauvegarder(operation)

    def _executer_et_sauvegarder(self, operation: Callable[[], None]) -> None:
        livres_avant = copy.deepcopy(self.livres)
        utilisateurs_avant = copy.deepcopy(self.utilisateurs)

        try:
            operation()
            self.sauvegarder()
        except Exception:
            self.livres = livres_avant
            self.utilisateurs = utilisateurs_avant
            raise

    @staticmethod
    def _champ_obligatoire(valeur: str, nom: str) -> str:
        valeur = (valeur or "").strip()
        if not valeur:
            raise ErreurBibliotheque(f"Le champ « {nom} » est obligatoire.")
        if "|" in valeur:
            raise ErreurBibliotheque(
                f"Le champ « {nom} » ne peut pas contenir le caractère « | »."
            )
        return valeur

    def _valider_livre(
        self, titre: str, auteur: str, isbn: str
    ) -> tuple[str, str, str]:
        titre_valide = self._champ_obligatoire(titre, "Titre")
        auteur_valide = self._champ_obligatoire(auteur, "Auteur")
        isbn_valide = self._champ_obligatoire(isbn, "ISBN")

        if "," in isbn_valide:
            raise ErreurBibliotheque(
                "L'ISBN ne peut pas contenir le caractère « , »."
            )

        return titre_valide, auteur_valide, isbn_valide

    def _valider_utilisateur(self, nom: str, identifiant: str) -> tuple[str, str]:
        nom_valide = self._champ_obligatoire(nom, "Nom")
        identifiant_valide = self._champ_obligatoire(identifiant, "ID utilisateur")
        return nom_valide, identifiant_valide
