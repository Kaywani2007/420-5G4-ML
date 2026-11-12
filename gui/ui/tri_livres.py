from __future__ import annotations

from collections.abc import Iterable

from bibliotheque.modeles import Livre
from bibliotheque.texte import normaliser_texte

__all__ = ["cle_tri_livre", "normaliser_texte", "trier_livres"]


def cle_tri_livre(livre: Livre, critere: str) -> tuple[str, str, str]:
    titre = normaliser_texte(livre.titre)
    auteur = normaliser_texte(livre.auteur)
    isbn = normaliser_texte(livre.isbn)

    if critere == "Auteur":
        return auteur, titre, isbn
    return titre, auteur, isbn


def trier_livres(
    livres: Iterable[Livre], critere: str
) -> list[Livre]:
    return sorted(livres, key=lambda livre: cle_tri_livre(livre, critere))
