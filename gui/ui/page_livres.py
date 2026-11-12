from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from bibliotheque.modeles import Livre
from bibliotheque.service import Bibliotheque, ErreurBibliotheque

from .composants import TableauDonnees
from .dialogues import demander_ajout_livre


class PageLivres(ctk.CTkFrame):
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
        self.grid_rowconfigure(2, weight=1)

        self._construire_entete()
        self._construire_barre_outils()
        self._construire_tableau()

    def _construire_entete(self) -> None:
        entete = ctk.CTkFrame(self, fg_color="transparent")
        entete.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        entete.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            entete,
            text="Livres",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self._compteur = ctk.CTkLabel(
            entete,
            text="0 livre",
            font=ctk.CTkFont(size=13),
            text_color=("gray35", "gray70"),
            anchor="w",
        )
        self._compteur.grid(row=1, column=0, sticky="w", pady=(2, 0))

        actions = ctk.CTkFrame(entete, fg_color="transparent")
        actions.grid(row=0, column=1, rowspan=2, sticky="e")

        ctk.CTkButton(
            actions,
            text="Ajouter un livre",
            width=140,
            command=self._ajouter_livre,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            actions,
            text="Supprimer le livre",
            width=150,
            fg_color="#9e3b3b",
            hover_color="#7f2f2f",
            command=self._supprimer_livre,
        ).pack(side="left")

    def _construire_barre_outils(self) -> None:
        barre = ctk.CTkFrame(self, corner_radius=12)
        barre.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        barre.grid_columnconfigure(0, weight=1)

        self._recherche = ctk.CTkEntry(
            barre,
            placeholder_text="Rechercher un livre...",
            height=36,
        )
        self._recherche.grid(
            row=0, column=0, sticky="ew", padx=(12, 8), pady=12
        )
        self._recherche.bind("<Return>", lambda _event: self.rafraichir())

        self._critere = ctk.CTkOptionMenu(
            barre,
            values=["Titre", "Auteur"],
            width=110,
            height=36,
        )
        self._critere.grid(row=0, column=1, padx=(0, 8), pady=12)

        self._filtre = ctk.CTkOptionMenu(
            barre,
            values=["Tous", "Disponibles", "Empruntés"],
            width=140,
            height=36,
            command=lambda _valeur: self.rafraichir(),
        )
        self._filtre.grid(row=0, column=2, padx=(0, 8), pady=12)

        ctk.CTkButton(
            barre,
            text="Rechercher",
            width=110,
            height=36,
            command=self.rafraichir,
        ).grid(row=0, column=3, padx=(0, 8), pady=12)

        ctk.CTkButton(
            barre,
            text="Réinitialiser",
            width=110,
            height=36,
            fg_color="transparent",
            border_width=1,
            command=self._reinitialiser,
        ).grid(row=0, column=4, padx=(0, 12), pady=12)

    def _construire_tableau(self) -> None:
        self._tableau = TableauDonnees(
            self,
            colonnes=[
                ("titre", "Titre", 230),
                ("auteur", "Auteur", 190),
                ("isbn", "ISBN", 150),
                ("statut", "Statut", 110),
                ("emprunteur", "Emprunteur", 190),
            ],
            hauteur=14,
        )
        self._tableau.grid(row=2, column=0, sticky="nsew")

    def rafraichir(self) -> None:
        texte = self._recherche.get().strip()
        critere = self._critere.get()
        filtre = self._filtre.get()

        if critere == "Auteur":
            livres = self.bibliotheque.rechercher_par_auteur(texte)
        else:
            livres = self.bibliotheque.rechercher_par_titre(texte)

        if filtre == "Disponibles":
            livres = [livre for livre in livres if livre.disponible]
        elif filtre == "Empruntés":
            livres = [livre for livre in livres if not livre.disponible]

        self._tableau.remplir(
            livres,
            self._formater_livre,
            tag_fonction=lambda livre: not livre.disponible,
        )

        nombre = len(livres)
        self._compteur.configure(
            text=f"{nombre} livre{'s' if nombre > 1 else ''} affiché"
            f"{'s' if nombre > 1 else ''}"
        )

    def _formater_livre(self, livre: Livre) -> tuple[str, ...]:
        emprunteur = livre.id_emprunteur
        if emprunteur:
            utilisateur = self.bibliotheque.trouver_utilisateur(emprunteur)
            if utilisateur is not None:
                emprunteur = f"{utilisateur.nom} ({emprunteur})"

        return (
            livre.titre,
            livre.auteur,
            livre.isbn,
            livre.statut,
            emprunteur,
        )

    def _ajouter_livre(self) -> None:
        donnees = demander_ajout_livre(self, self.bibliotheque)
        if donnees is None:
            return

        try:
            livre = self.bibliotheque.ajouter_livre(
                donnees["titre"],
                donnees["auteur"],
                donnees["isbn"],
            )
        except ErreurBibliotheque as exc:
            messagebox.showerror(
                "Erreur",
                str(exc),
                parent=self.winfo_toplevel(),
            )
            return

        self._apres_mutation(f"Livre « {livre.titre} » ajouté avec succès.")

    def _supprimer_livre(self) -> None:
        livre = self._tableau.selection()
        if livre is None:
            messagebox.showinfo(
                "Information",
                "Veuillez sélectionner un livre à supprimer.",
                parent=self.winfo_toplevel(),
            )
            return

        confirmation = messagebox.askyesno(
            "Confirmer la suppression",
            f"Supprimer le livre « {livre.titre} » (ISBN : {livre.isbn}) ?",
            parent=self.winfo_toplevel(),
        )
        if not confirmation:
            return

        try:
            self.bibliotheque.supprimer_livre(livre.isbn)
        except ErreurBibliotheque as exc:
            messagebox.showerror(
                "Erreur",
                str(exc),
                parent=self.winfo_toplevel(),
            )
            return

        self._apres_mutation(f"Livre « {livre.titre} » supprimé avec succès.")

    def _reinitialiser(self) -> None:
        self._recherche.delete(0, "end")
        self._critere.set("Titre")
        self._filtre.set("Tous")
        self.rafraichir()
