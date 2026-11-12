from __future__ import annotations

import unittest

from bibliotheque.modeles import Livre
from ui.tri_livres import normaliser_texte, trier_livres


class TestTriLivres(unittest.TestCase):
    def test_tri_par_titre_sans_retirer_les_articles(self) -> None:
        livres = [
            Livre("Livre", "Auteur", "ISBN-2"),
            Livre("Le Zèbre", "Auteur", "ISBN-1"),
        ]

        resultat = trier_livres(livres, "Titre")

        self.assertEqual(
            [livre.titre for livre in resultat],
            ["Le Zèbre", "Livre"],
        )

    def test_tri_par_auteur_sur_le_nom_complet(self) -> None:
        livres = [
            Livre("Livre 1", "Victor Hugo", "ISBN-1"),
            Livre("Livre 2", "Émile Zola", "ISBN-2"),
            Livre("Livre 3", "Albert Camus", "ISBN-3"),
        ]

        resultat = trier_livres(livres, "Auteur")

        self.assertEqual(
            [livre.auteur for livre in resultat],
            ["Albert Camus", "Émile Zola", "Victor Hugo"],
        )

    def test_tri_ignore_la_casse_et_les_accents(self) -> None:
        livres = [
            Livre("Zola", "Auteur", "ISBN-3"),
            Livre("Étranger", "Auteur", "ISBN-2"),
            Livre("apple", "Auteur", "ISBN-1"),
        ]

        resultat = trier_livres(livres, "Titre")

        self.assertEqual(
            [livre.titre for livre in resultat],
            ["apple", "Étranger", "Zola"],
        )

    def test_normalisation_des_ligatures(self) -> None:
        self.assertEqual(normaliser_texte("Œuvre"), "oeuvre")
        self.assertEqual(normaliser_texte("Cœur"), "coeur")

    def test_tri_avec_departage_par_titre_puis_isbn(self) -> None:
        livres = [
            Livre("Même titre", "Zoé", "ISBN-3"),
            Livre("Même titre", "Alice", "ISBN-2"),
            Livre("Même titre", "Alice", "ISBN-1"),
        ]

        resultat = trier_livres(livres, "Auteur")

        self.assertEqual(
            [livre.isbn for livre in resultat],
            ["ISBN-1", "ISBN-2", "ISBN-3"],
        )


if __name__ == "__main__":
    unittest.main()
