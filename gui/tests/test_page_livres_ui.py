from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

try:
    import customtkinter as ctk
except ImportError:
    ctk = None


@unittest.skipIf(ctk is None, "customtkinter n'est pas installé")
class TestPageLivresUI(unittest.TestCase):
    def setUp(self) -> None:
        from bibliotheque.service import Bibliotheque
        from bibliotheque.stockage import Stockage
        from ui.page_livres import PageLivres

        self.dossier = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dossier)

        chemin_livres = self.dossier / "books.txt"
        chemin_utilisateurs = self.dossier / "users.txt"
        chemin_livres.write_text(
            "Zola|Émile Zola|ISBN-3|1|\n"
            "Les Misérables|Victor Hugo|ISBN-2|0|U1\n"
            "Le Petit Prince|Antoine de Saint-Exupéry|ISBN-1|1|\n",
            encoding="utf-8",
        )
        chemin_utilisateurs.write_text(
            "Alice|U1|ISBN-2\n",
            encoding="utf-8",
        )

        self.bibliotheque = Bibliotheque(
            Stockage(chemin_livres, chemin_utilisateurs)
        )
        self.bibliotheque.charger()

        try:
            self.racine = ctk.CTk()
        except Exception as exc:
            self.skipTest(f"Affichage graphique indisponible : {exc}")

        self.addCleanup(self.racine.destroy)
        self.racine.withdraw()
        self.page = PageLivres(self.racine, self.bibliotheque, lambda _message: None)
        self.page.pack(fill="both", expand=True)
        self.page.rafraichir()
        self.racine.update()

    def _titres_affiches(self) -> list[str]:
        return [
            self.page._tableau.arbres.item(iid, "values")[0]
            for iid in self.page._tableau.arbres.get_children()
        ]

    def _rechercher(self, texte: str, critere: str, filtre: str = "Tous") -> None:
        self.page._recherche.delete(0, "end")
        if texte:
            self.page._recherche.insert(0, texte)
        self.page._critere.set(critere)
        self.page._filtre.set(filtre)
        self.page._rechercher()
        self.racine.update()

    def test_champ_vide_trie_par_titre(self) -> None:
        self._rechercher("", "Titre")

        self.assertEqual(
            self._titres_affiches(),
            ["Le Petit Prince", "Les Misérables", "Zola"],
        )
        self.assertEqual(
            self.page._compteur.cget("text"),
            "3 livres affichés",
        )

    def test_champ_vide_trie_par_auteur(self) -> None:
        self._rechercher("", "Auteur")

        self.assertEqual(
            self._titres_affiches(),
            ["Le Petit Prince", "Zola", "Les Misérables"],
        )

    def test_changement_de_critere_sans_recherche_ne_modifie_pas_le_tableau(
        self,
    ) -> None:
        self._rechercher("", "Titre")
        titres_avant = self._titres_affiches()

        self.page._critere.set("Auteur")
        self.racine.update()

        self.assertEqual(self._titres_affiches(), titres_avant)

    def test_recherche_par_titre(self) -> None:
        self._rechercher("miser", "Titre")

        self.assertEqual(self._titres_affiches(), ["Les Misérables"])

    def test_recherche_par_auteur(self) -> None:
        self._rechercher("hugo", "Auteur")

        self.assertEqual(self._titres_affiches(), ["Les Misérables"])

    def test_resultats_de_recherche_tries(self) -> None:
        self._rechercher("e", "Titre")

        self.assertEqual(
            self._titres_affiches(),
            ["Le Petit Prince", "Les Misérables"],
        )

    def test_tri_combine_au_filtre_de_disponibilite(self) -> None:
        self._rechercher("", "Titre", "Disponibles")
        self.assertEqual(
            self._titres_affiches(),
            ["Le Petit Prince", "Zola"],
        )

        self._rechercher("", "Titre", "Empruntés")
        self.assertEqual(self._titres_affiches(), ["Les Misérables"])

    def test_message_aucun_resultat(self) -> None:
        self._rechercher("introuvable", "Titre")

        self.assertEqual(self._titres_affiches(), [])
        self.assertEqual(
            self.page._message_vide.cget("text"),
            "Aucun livre ne correspond à votre recherche.",
        )
        self.assertEqual(self.page._compteur.cget("text"), "0 livre affiché")

    def test_reinitialisation(self) -> None:
        self._rechercher("hugo", "Auteur", "Empruntés")
        self.assertEqual(self._titres_affiches(), ["Les Misérables"])

        self.page._reinitialiser()
        self.racine.update()

        self.assertEqual(self.page._recherche.get(), "")
        self.assertEqual(self.page._critere.get(), "Titre")
        self.assertEqual(self.page._filtre.get(), "Tous")
        self.assertEqual(
            self._titres_affiches(),
            ["Le Petit Prince", "Les Misérables", "Zola"],
        )


if __name__ == "__main__":
    unittest.main()
