from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from bibliotheque.modeles import Utilisateur
from bibliotheque.service import Bibliotheque, ErreurBibliotheque

from .composants import TableauDonnees
from .dialogues import demander_ajout_utilisateur


class PageUtilisateurs(ctk.CTkFrame):
    def __init__(
        self,
        master: Any,
        bibliotheque: Bibliotheque,
        apres_mutation: Callable[[str], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.bibliotheque = bibliotheque
        self._apres_mutation = apres_mutation

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construire_entete()
        self._construire_tableau()

    def _construire_entete(self) -> None:
        entete = ctk.CTkFrame(self, fg_color="transparent")
        entete.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        entete.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            entete,
            text="Utilisateurs",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self._compteur = ctk.CTkLabel(
            entete,
            text="0 utilisateur",
            font=ctk.CTkFont(size=13),
            text_color=("gray35", "gray70"),
            anchor="w",
        )
        self._compteur.grid(row=1, column=0, sticky="w", pady=(2, 0))

        ctk.CTkButton(
            entete,
            text="Ajouter un utilisateur",
            width=180,
            command=self._ajouter_utilisateur,
        ).grid(row=0, column=1, rowspan=2, sticky="e")

    def _construire_tableau(self) -> None:
        self._tableau = TableauDonnees(
            self,
            colonnes=[
                ("nom", "Nom", 230),
                ("identifiant", "ID", 150),
                ("nombre", "Emprunts", 110),
                ("isbns", "ISBN empruntés", 350),
            ],
            hauteur=14,
        )
        self._tableau.grid(row=1, column=0, sticky="nsew")

    def rafraichir(self) -> None:
        utilisateurs = self.bibliotheque.utilisateurs
        self._tableau.remplir(
            utilisateurs,
            self._formater_utilisateur,
            tag_fonction=lambda utilisateur: bool(utilisateur.isbns_empruntes),
        )

        nombre = len(utilisateurs)
        self._compteur.configure(
            text=f"{nombre} utilisateur{'s' if nombre > 1 else ''}"
        )

    @staticmethod
    def _formater_utilisateur(utilisateur: Utilisateur) -> tuple[str, ...]:
        isbns = ", ".join(utilisateur.isbns_empruntes) or "—"
        return (
            utilisateur.nom,
            utilisateur.identifiant,
            str(utilisateur.nombre_emprunts),
            isbns,
        )

    def _ajouter_utilisateur(self) -> None:
        donnees = demander_ajout_utilisateur(self, self.bibliotheque)
        if donnees is None:
            return

        try:
            utilisateur = self.bibliotheque.ajouter_utilisateur(
                donnees["nom"],
                donnees["identifiant"],
            )
        except ErreurBibliotheque as exc:
            messagebox.showerror(
                "Erreur",
                str(exc),
                parent=self.winfo_toplevel(),
            )
            return

        self._apres_mutation(
            f"Utilisateur « {utilisateur.nom} » ajouté avec succès."
        )
