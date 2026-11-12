from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Livre:
    titre: str
    auteur: str
    isbn: str
    disponible: bool = True
    id_emprunteur: str = ""

    @property
    def statut(self) -> str:
        return "Disponible" if self.disponible else "Emprunté"

    def to_file_line(self) -> str:
        disponibilite = "1" if self.disponible else "0"
        return f"{self.titre}|{self.auteur}|{self.isbn}|{disponibilite}|{self.id_emprunteur}"

    @classmethod
    def from_file_line(cls, ligne: str) -> "Livre":
        parties = ligne.rstrip("\r\n").split("|", 4)
        parties += [""] * (5 - len(parties))
        titre, auteur, isbn, disponibilite, id_emprunteur = parties[:5]
        return cls(
            titre=titre,
            auteur=auteur,
            isbn=isbn,
            disponible=disponibilite == "1",
            id_emprunteur=id_emprunteur,
        )

    def marquer_emprunte(self, id_emprunteur: str) -> None:
        self.disponible = False
        self.id_emprunteur = id_emprunteur

    def marquer_retourne(self) -> None:
        self.disponible = True
        self.id_emprunteur = ""


@dataclass
class Utilisateur:
    nom: str
    identifiant: str
    isbns_empruntes: list[str] = field(default_factory=list)

    def to_file_line(self) -> str:
        return f"{self.nom}|{self.identifiant}|{','.join(self.isbns_empruntes)}"

    @classmethod
    def from_file_line(cls, ligne: str) -> "Utilisateur":
        parties = ligne.rstrip("\r\n").split("|", 2)
        parties += [""] * (3 - len(parties))
        nom, identifiant, isbns = parties[:3]
        liste_isbns = [isbn.strip() for isbn in isbns.split(",") if isbn.strip()]
        return cls(nom=nom, identifiant=identifiant, isbns_empruntes=liste_isbns)

    def a_emprunte(self, isbn: str) -> bool:
        return isbn in self.isbns_empruntes

    def ajouter_emprunt(self, isbn: str) -> None:
        if not self.a_emprunte(isbn):
            self.isbns_empruntes.append(isbn)

    def retirer_emprunt(self, isbn: str) -> None:
        if self.a_emprunte(isbn):
            self.isbns_empruntes.remove(isbn)

    @property
    def nombre_emprunts(self) -> int:
        return len(self.isbns_empruntes)
