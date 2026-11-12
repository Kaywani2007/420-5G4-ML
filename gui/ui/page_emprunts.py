from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from bibliotheque.modeles import Livre, Utilisateur
from bibliotheque.service import Bibliotheque, ErreurBibliotheque

from .composants import TableauDonnees


class PageEmprunts(ctk.CTkFrame):
    def __init__(
        self,
        master: Any,
        bibliotheque: Bibliotheque,
        apres_mutation: Callable[[str], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.bibliotheque = bibliotheque
        self._apres_mutation = apres_mutation

        self._livres_par_affichage: dict[str, Livre] = {}
        self._utilisateurs_par_affichage: dict[str, Utilisateur] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construire_entete()
        self._construire_contenu()

    def _construire_entete(self) -> None:
        entete = ctk.CTkFrame(self, fg_color="transparent")
        entete.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(
            entete,
            text="Emprunts et retours",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            entete,
            text="Gérez les prêts de livres entre la bibliothèque et ses utilisateurs.",
            font=ctk.CTkFont(size=13),
            text_color=("gray35", "gray70"),
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

    def _construire_contenu(self) -> None:
        contenu = ctk.CTkFrame(self, fg_color="transparent")
        contenu.grid(row=1, column=0, sticky="nsew")
        contenu.grid_columnconfigure(0, weight=0)
        contenu.grid_columnconfigure(1, weight=1)
        contenu.grid_rowconfigure(0, weight=1)

        self._construire_emprunt(contenu)
        self._construire_retour(contenu)

    def _construire_emprunt(self, parent: ctk.CTkFrame) -> None:
        cadre = ctk.CTkFrame(parent, corner_radius=12, width=330)
        cadre.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        cadre.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cadre,
            text="Emprunter un livre",
            font=ctk.CTkFont(size=19, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 4))

        ctk.CTkLabel(
            cadre,
            text="Livre disponible",
            font=ctk.CTkFont(size=13),
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(14, 4))

        self._choix_livre = ctk.CTkOptionMenu(
            cadre,
            values=["Aucun livre disponible"],
            height=36,
            anchor="w",
        )
        self._choix_livre.grid(row=2, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(
            cadre,
            text="Utilisateur",
            font=ctk.CTkFont(size=13),
            anchor="w",
        ).grid(row=3, column=0, sticky="ew", padx=18, pady=(16, 4))

        self._choix_utilisateur = ctk.CTkOptionMenu(
            cadre,
            values=["Aucun utilisateur"],
            height=36,
            anchor="w",
        )
        self._choix_utilisateur.grid(row=4, column=0, sticky="ew", padx=18)

        self._bouton_emprunter = ctk.CTkButton(
            cadre,
            text="Emprunter",
            height=40,
            command=self._emprunter,
        )
        self._bouton_emprunter.grid(
            row=5, column=0, sticky="ew", padx=18, pady=(24, 10)
        )

        self._info_emprunt = ctk.CTkLabel(
            cadre,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray35", "gray70"),
            anchor="w",
            justify="left",
            wraplength=280,
        )
        self._info_emprunt.grid(
            row=6, column=0, sticky="ew", padx=18, pady=(0, 18)
        )

    def _construire_retour(self, parent: ctk.CTkFrame) -> None:
        cadre = ctk.CTkFrame(parent, corner_radius=12)
        cadre.grid(row=0, column=1, sticky="nsew")
        cadre.grid_columnconfigure(0, weight=1)
        cadre.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            cadre,
            text="Retourner un livre",
            font=ctk.CTkFont(size=19, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 4))

        ctk.CTkLabel(
            cadre,
            text="Sélectionnez un livre actuellement emprunté.",
            font=ctk.CTkFont(size=13),
            text_color=("gray35", "gray70"),
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))

        self._tableau_retours = TableauDonnees(
            cadre,
            colonnes=[
                ("titre", "Titre", 250),
                ("isbn", "ISBN", 160),
                ("emprunteur", "Emprunteur", 190),
            ],
            hauteur=11,
        )
        self._tableau_retours.grid(
            row=2, column=0, sticky="nsew", padx=18, pady=(0, 10)
        )

        self._bouton_retourner = ctk.CTkButton(
            cadre,
            text="Retourner le livre",
            height=40,
            command=self._retourner,
        )
        self._bouton_retourner.grid(
            row=3, column=0, sticky="ew", padx=18, pady=(0, 18)
        )

    def rafraichir(self) -> None:
        self._rafraichir_choix()
        self._rafraichir_retours()

    def _rafraichir_choix(self) -> None:
        livres = self.bibliotheque.livres_disponibles
        self._livres_par_affichage = {
            f"{livre.titre} — {livre.isbn}": livre for livre in livres
        }
        valeurs_livres = list(self._livres_par_affichage) or [
            "Aucun livre disponible"
        ]
        self._choix_livre.configure(values=valeurs_livres)
        if self._choix_livre.get() not in valeurs_livres:
            self._choix_livre.set(valeurs_livres[0])

        utilisateurs = self.bibliotheque.utilisateurs
        self._utilisateurs_par_affichage = {
            f"{utilisateur.nom} — {utilisateur.identifiant}": utilisateur
            for utilisateur in utilisateurs
        }
        valeurs_utilisateurs = list(self._utilisateurs_par_affichage) or [
            "Aucun utilisateur"
        ]
        self._choix_utilisateur.configure(values=valeurs_utilisateurs)
        if self._choix_utilisateur.get() not in valeurs_utilisateurs:
            self._choix_utilisateur.set(valeurs_utilisateurs[0])

        emprunt_possible = bool(livres) and bool(utilisateurs)
        self._bouton_emprunter.configure(
            state="normal" if emprunt_possible else "disabled"
        )
        self._info_emprunt.configure(
            text=(
                f"{len(livres)} livre{'s' if len(livres) > 1 else ''} "
                f"disponible{'s' if len(livres) > 1 else ''} · "
                f"{len(utilisateurs)} utilisateur"
                f"{'s' if len(utilisateurs) > 1 else ''} enregistré"
                f"{'s' if len(utilisateurs) > 1 else ''}."
            )
        )

    def _rafraichir_retours(self) -> None:
        livres = self.bibliotheque.livres_empruntes
        self._tableau_retours.remplir(
            livres,
            self._formater_retour,
            tag_fonction=lambda _livre: True,
        )
        self._bouton_retourner.configure(
            state="normal" if livres else "disabled"
        )

    def _formater_retour(self, livre: Livre) -> tuple[str, ...]:
        emprunteur = livre.id_emprunteur
        utilisateur = self.bibliotheque.trouver_utilisateur(emprunteur)
        if utilisateur is not None:
            emprunteur = f"{utilisateur.nom} ({emprunteur})"
        return (livre.titre, livre.isbn, emprunteur)

    def _emprunter(self) -> None:
        livre = self._livres_par_affichage.get(self._choix_livre.get())
        utilisateur = self._utilisateurs_par_affichage.get(
            self._choix_utilisateur.get()
        )

        if livre is None or utilisateur is None:
            messagebox.showinfo(
                "Information",
                "Veuillez sélectionner un livre disponible et un utilisateur.",
                parent=self.winfo_toplevel(),
            )
            return

        try:
            self.bibliotheque.emprunter(livre.isbn, utilisateur.identifiant)
        except ErreurBibliotheque as exc:
            messagebox.showerror(
                "Erreur",
                str(exc),
                parent=self.winfo_toplevel(),
            )
            return

        self._apres_mutation(
            f"« {livre.titre} » emprunté par {utilisateur.nom}."
        )

    def _retourner(self) -> None:
        livre = self._tableau_retours.selection()
        if livre is None:
            messagebox.showinfo(
                "Information",
                "Veuillez sélectionner un livre à retourner.",
                parent=self.winfo_toplevel(),
            )
            return

        confirmation = messagebox.askyesno(
            "Confirmer le retour",
            f"Retourner le livre « {livre.titre} » (ISBN : {livre.isbn}) ?",
            parent=self.winfo_toplevel(),
        )
        if not confirmation:
            return

        try:
            self.bibliotheque.retourner(livre.isbn)
        except ErreurBibliotheque as exc:
            messagebox.showerror(
                "Erreur",
                str(exc),
                parent=self.winfo_toplevel(),
            )
            return

        self._apres_mutation(f"« {livre.titre} » retourné avec succès.")
