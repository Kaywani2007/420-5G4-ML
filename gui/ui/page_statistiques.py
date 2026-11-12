from __future__ import annotations

from typing import Any

import customtkinter as ctk

from bibliotheque.service import Bibliotheque

from .composants import CarteStatistique


class PageStatistiques(ctk.CTkFrame):
    def __init__(self, master: Any, bibliotheque: Bibliotheque) -> None:
        super().__init__(master, fg_color="transparent")
        self.bibliotheque = bibliotheque

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._construire_entete()
        self._construire_cartes()
        self._construire_fichiers()

    def _construire_entete(self) -> None:
        entete = ctk.CTkFrame(self, fg_color="transparent")
        entete.grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14)
        )

        ctk.CTkLabel(
            entete,
            text="Statistiques",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            entete,
            text="Vue d'ensemble de l'état actuel de la bibliothèque.",
            font=ctk.CTkFont(size=13),
            text_color=("gray35", "gray70"),
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

    def _construire_cartes(self) -> None:
        self._carte_total = CarteStatistique(
            self,
            "Total des livres",
            couleur="#1f6aa5",
        )
        self._carte_total.grid(
            row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 12)
        )

        self._carte_disponibles = CarteStatistique(
            self,
            "Livres disponibles",
            couleur="#2fa572",
        )
        self._carte_disponibles.grid(
            row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 12)
        )

        self._carte_empruntes = CarteStatistique(
            self,
            "Livres empruntés",
            couleur="#c46a2d",
        )
        self._carte_empruntes.grid(
            row=2, column=0, sticky="new", padx=(0, 8), pady=(0, 12)
        )

        self._carte_utilisateurs = CarteStatistique(
            self,
            "Total des utilisateurs",
            couleur="#8a5cb8",
        )
        self._carte_utilisateurs.grid(
            row=2, column=1, sticky="new", padx=(8, 0), pady=(0, 12)
        )

    def _construire_fichiers(self) -> None:
        cadre = ctk.CTkFrame(self, corner_radius=12)
        cadre.grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(4, 0)
        )
        cadre.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            cadre,
            text="Fichiers de données",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(16, 6))

        ctk.CTkLabel(
            cadre,
            text="Livres :",
            font=ctk.CTkFont(size=13),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=(18, 8), pady=2)

        self._chemin_livres = ctk.CTkLabel(
            cadre,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=("gray35", "gray70"),
            anchor="w",
        )
        self._chemin_livres.grid(row=1, column=1, sticky="ew", padx=(0, 18), pady=2)

        ctk.CTkLabel(
            cadre,
            text="Utilisateurs :",
            font=ctk.CTkFont(size=13),
            anchor="w",
        ).grid(row=2, column=0, sticky="w", padx=(18, 8), pady=(2, 16))

        self._chemin_utilisateurs = ctk.CTkLabel(
            cadre,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=("gray35", "gray70"),
            anchor="w",
        )
        self._chemin_utilisateurs.grid(
            row=2, column=1, sticky="ew", padx=(0, 18), pady=(2, 16)
        )

    def rafraichir(self) -> None:
        self._carte_total.definir_valeur(self.bibliotheque.total_livres)
        self._carte_disponibles.definir_valeur(
            self.bibliotheque.total_disponibles
        )
        self._carte_empruntes.definir_valeur(self.bibliotheque.total_empruntes)
        self._carte_utilisateurs.definir_valeur(
            self.bibliotheque.total_utilisateurs
        )

        stockage = self.bibliotheque.stockage
        self._chemin_livres.configure(text=str(stockage.chemin_livres))
        self._chemin_utilisateurs.configure(
            text=str(stockage.chemin_utilisateurs)
        )
