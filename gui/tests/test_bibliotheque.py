from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from bibliotheque.service import Bibliotheque, ErreurBibliotheque
from bibliotheque.stockage import Stockage


class TestStockage(unittest.TestCase):
    def setUp(self) -> None:
        self.dossier = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dossier)

        self.chemin_livres = self.dossier / "books.txt"
        self.chemin_utilisateurs = self.dossier / "users.txt"

        self.chemin_livres.write_text(
            "Le Petit Prince|Antoine de Saint-Exupéry|9782070612758|1|\n"
            "Les Misérables|Victor Hugo|9782253096337|0|USR001\n",
            encoding="utf-8",
        )
        self.chemin_utilisateurs.write_text(
            "Marie Dubois|USR001|9782253096337\n"
            "Alexandra Dumont|USR015|\n",
            encoding="utf-8",
        )

    def test_chargement_des_formats_actuels(self) -> None:
        stockage = Stockage(self.chemin_livres, self.chemin_utilisateurs)

        livres = stockage.charger_livres()
        utilisateurs = stockage.charger_utilisateurs()

        self.assertEqual(len(livres), 2)
        self.assertEqual(livres[0].titre, "Le Petit Prince")
        self.assertTrue(livres[0].disponible)
        self.assertEqual(livres[1].id_emprunteur, "USR001")
        self.assertFalse(livres[1].disponible)

        self.assertEqual(len(utilisateurs), 2)
        self.assertEqual(utilisateurs[0].isbns_empruntes, ["9782253096337"])
        self.assertEqual(utilisateurs[1].isbns_empruntes, [])

    def test_sauvegarde_recharge_sans_perte(self) -> None:
        stockage = Stockage(self.chemin_livres, self.chemin_utilisateurs)
        livres = stockage.charger_livres()
        utilisateurs = stockage.charger_utilisateurs()

        stockage.sauvegarder(livres, utilisateurs)

        self.assertEqual(
            self.chemin_livres.read_text(encoding="utf-8"),
            "Le Petit Prince|Antoine de Saint-Exupéry|9782070612758|1|\n"
            "Les Misérables|Victor Hugo|9782253096337|0|USR001\n",
        )
        self.assertEqual(
            self.chemin_utilisateurs.read_text(encoding="utf-8"),
            "Marie Dubois|USR001|9782253096337\n"
            "Alexandra Dumont|USR015|\n",
        )

    def test_conserve_les_fins_de_ligne_crlf(self) -> None:
        self.chemin_livres.write_bytes(
            (
                "Le Petit Prince|Antoine de Saint-Exupéry|9782070612758|1|\r\n"
                "Les Misérables|Victor Hugo|9782253096337|0|USR001\r\n"
            ).encode("utf-8")
        )
        self.chemin_utilisateurs.write_bytes(
            (
                "Marie Dubois|USR001|9782253096337\r\n"
                "Alexandra Dumont|USR015|\r\n"
            ).encode("utf-8")
        )

        stockage = Stockage(self.chemin_livres, self.chemin_utilisateurs)
        stockage.sauvegarder(
            stockage.charger_livres(),
            stockage.charger_utilisateurs(),
        )

        self.assertTrue(
            self.chemin_livres.read_bytes().endswith(b"\r\n")
        )
        self.assertTrue(
            self.chemin_utilisateurs.read_bytes().endswith(b"\r\n")
        )

    def test_fichiers_absents_retournent_listes_vides(self) -> None:
        stockage = Stockage(
            self.dossier / "absent_books.txt",
            self.dossier / "absent_users.txt",
        )
        self.assertEqual(stockage.charger_livres(), [])
        self.assertEqual(stockage.charger_utilisateurs(), [])

    def test_creation_des_fichiers_backup(self) -> None:
        stockage = Stockage(self.chemin_livres, self.chemin_utilisateurs)
        copies = stockage.creer_sauvegarde()

        self.assertEqual(len(copies), 2)
        self.assertTrue((self.dossier / "books.txt.backup").exists())
        self.assertTrue((self.dossier / "users.txt.backup").exists())


class TestBibliotheque(unittest.TestCase):
    def setUp(self) -> None:
        self.dossier = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dossier)

        self.chemin_livres = self.dossier / "books.txt"
        self.chemin_utilisateurs = self.dossier / "users.txt"

        self.chemin_livres.write_text(
            "Livre A|Auteur A|ISBN-A|1|\n"
            "Livre B|Auteur B|ISBN-B|0|U1\n",
            encoding="utf-8",
        )
        self.chemin_utilisateurs.write_text(
            "Alice|U1|ISBN-B\n"
            "Bob|U2|\n",
            encoding="utf-8",
        )

        self.bibliotheque = Bibliotheque(
            Stockage(self.chemin_livres, self.chemin_utilisateurs)
        )
        self.bibliotheque.charger()

    def _recharger(self) -> Bibliotheque:
        bibliotheque = Bibliotheque(
            Stockage(self.chemin_livres, self.chemin_utilisateurs)
        )
        bibliotheque.charger()
        return bibliotheque

    def test_recherche_insensible_a_la_casse(self) -> None:
        self.assertEqual(
            [livre.isbn for livre in self.bibliotheque.rechercher_par_titre("livre")],
            ["ISBN-A", "ISBN-B"],
        )
        self.assertEqual(
            [
                livre.isbn
                for livre in self.bibliotheque.rechercher_par_auteur("auteur b")
            ],
            ["ISBN-B"],
        )

    def test_ajout_livre_et_refus_doublon(self) -> None:
        self.bibliotheque.ajouter_livre("Livre C", "Auteur C", "ISBN-C")

        rechargee = self._recharger()
        self.assertIsNotNone(rechargee.trouver_livre("ISBN-C"))

        with self.assertRaises(ErreurBibliotheque):
            self.bibliotheque.ajouter_livre("Doublon", "Auteur", "ISBN-C")

    def test_ajout_utilisateur_et_refus_doublon(self) -> None:
        self.bibliotheque.ajouter_utilisateur("Chloé", "U3")

        rechargee = self._recharger()
        self.assertIsNotNone(rechargee.trouver_utilisateur("U3"))

        with self.assertRaises(ErreurBibliotheque):
            self.bibliotheque.ajouter_utilisateur("Autre", "U3")

    def test_emprunt_met_a_jour_les_deux_fichiers(self) -> None:
        self.bibliotheque.emprunter("ISBN-A", "U2")

        rechargee = self._recharger()
        livre = rechargee.trouver_livre("ISBN-A")
        utilisateur = rechargee.trouver_utilisateur("U2")

        self.assertIsNotNone(livre)
        self.assertIsNotNone(utilisateur)
        self.assertFalse(livre.disponible)
        self.assertEqual(livre.id_emprunteur, "U2")
        self.assertIn("ISBN-A", utilisateur.isbns_empruntes)

    def test_emprunt_refuse_si_deja_emprunte(self) -> None:
        with self.assertRaises(ErreurBibliotheque):
            self.bibliotheque.emprunter("ISBN-B", "U2")

    def test_retour_met_a_jour_les_deux_fichiers(self) -> None:
        self.bibliotheque.retourner("ISBN-B")

        rechargee = self._recharger()
        livre = rechargee.trouver_livre("ISBN-B")
        utilisateur = rechargee.trouver_utilisateur("U1")

        self.assertIsNotNone(livre)
        self.assertIsNotNone(utilisateur)
        self.assertTrue(livre.disponible)
        self.assertEqual(livre.id_emprunteur, "")
        self.assertNotIn("ISBN-B", utilisateur.isbns_empruntes)

    def test_suppression_livre_disponible(self) -> None:
        self.bibliotheque.supprimer_livre("ISBN-A")

        rechargee = self._recharger()
        self.assertIsNone(rechargee.trouver_livre("ISBN-A"))

    def test_suppression_livre_emprunte_refusee(self) -> None:
        with self.assertRaises(ErreurBibliotheque):
            self.bibliotheque.supprimer_livre("ISBN-B")

    def test_champs_invalides_refuses(self) -> None:
        with self.assertRaises(ErreurBibliotheque):
            self.bibliotheque.ajouter_livre("Titre|invalide", "Auteur", "ISBN-D")

        with self.assertRaises(ErreurBibliotheque):
            self.bibliotheque.ajouter_livre("Titre", "Auteur", "ISBN,D")

        with self.assertRaises(ErreurBibliotheque):
            self.bibliotheque.ajouter_livre("", "Auteur", "ISBN-E")


if __name__ == "__main__":
    unittest.main()
