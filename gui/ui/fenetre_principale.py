from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from bibliotheque.service import Bibliotheque, ErreurBibliotheque

from .page_emprunts import PageEmprunts
from .page_livres import PageLivres
from .page_statistiques import PageStatistiques
from .page_utilisateurs import PageUtilisateurs


class FenetrePrincipale(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Système de Gestion de Bibliothèque Personnelle")
        self.geometry("1180x760")
        self.minsize(1020, 660)

        self.bibliotheque = Bibliotheque()
        self._erreur_chargement: str | None = None

        try:
            self.bibliotheque.charger()
        except ErreurBibliotheque as exc:
            self._erreur_chargement = str(exc)

        self._pages: dict[str, ctk.CTkFrame] = {}
        self._boutons_navigation: dict[str, ctk.CTkButton] = {}

        self._construire_interface()
        self._afficher_page("livres")
        self.rafraichir_tout()
        self._definir_statut(
            f"Données chargées : {self.bibliotheque.total_livres} livres, "
            f"{self.bibliotheque.total_utilisateurs} utilisateurs."
        )

        self.protocol("WM_DELETE_WINDOW", self._fermer)

        if self._erreur_chargement is not None:
            self.after(250, self._afficher_erreur_chargement)

    def _construire_interface(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._construire_barre_laterale()
        self._construire_contenu()
        self._construire_barre_etat()

    def _construire_barre_laterale(self) -> None:
        self._barre_laterale = ctk.CTkFrame(
            self, width=230, corner_radius=0
        )
        self._barre_laterale.grid(row=0, column=0, sticky="nsew")
        self._barre_laterale.grid_columnconfigure(0, weight=1)
        self._barre_laterale.grid_rowconfigure(7, weight=1)

        ctk.CTkLabel(
            self._barre_laterale,
            text="Bibliothèque",
            font=ctk.CTkFont(size=23, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(22, 0))

        ctk.CTkLabel(
            self._barre_laterale,
            text="Gestion personnelle",
            font=ctk.CTkFont(size=12),
            text_color=("gray35", "gray70"),
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 20))

        entrees = [
            ("livres", "Livres"),
            ("utilisateurs", "Utilisateurs"),
            ("emprunts", "Emprunts et retours"),
            ("statistiques", "Statistiques"),
        ]

        for index, (cle, libelle) in enumerate(entrees, start=2):
            bouton = ctk.CTkButton(
                self._barre_laterale,
                text=libelle,
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                command=lambda nom=cle: self._afficher_page(nom),
            )
            bouton.grid(
                row=index, column=0, sticky="ew", padx=12, pady=3
            )
            self._boutons_navigation[cle] = bouton

        ctk.CTkButton(
            self._barre_laterale,
            text="Sauvegarder les données",
            height=38,
            command=self._sauvegarder,
        ).grid(row=8, column=0, sticky="ew", padx=14, pady=(0, 6))

        ctk.CTkButton(
            self._barre_laterale,
            text="Créer une sauvegarde",
            height=38,
            fg_color="transparent",
            border_width=1,
            command=self._creer_sauvegarde,
        ).grid(row=9, column=0, sticky="ew", padx=14, pady=(0, 14))

        ctk.CTkLabel(
            self._barre_laterale,
            text="Apparence",
            font=ctk.CTkFont(size=12),
            text_color=("gray35", "gray70"),
            anchor="w",
        ).grid(row=10, column=0, sticky="ew", padx=18, pady=(0, 4))

        self._apparence = ctk.CTkOptionMenu(
            self._barre_laterale,
            values=["Système", "Clair", "Sombre"],
            command=self._changer_apparence,
        )
        self._apparence.set("Système")
        self._apparence.grid(
            row=11, column=0, sticky="ew", padx=14, pady=(0, 18)
        )

    def _construire_contenu(self) -> None:
        self._contenu = ctk.CTkFrame(self, fg_color="transparent")
        self._contenu.grid(
            row=0, column=1, sticky="nsew", padx=24, pady=20
        )
        self._contenu.grid_rowconfigure(0, weight=1)
        self._contenu.grid_columnconfigure(0, weight=1)

        self._pages = {
            "livres": PageLivres(
                self._contenu,
                self.bibliotheque,
                self._apres_mutation,
            ),
            "utilisateurs": PageUtilisateurs(
                self._contenu,
                self.bibliotheque,
                self._apres_mutation,
            ),
            "emprunts": PageEmprunts(
                self._contenu,
                self.bibliotheque,
                self._apres_mutation,
            ),
            "statistiques": PageStatistiques(
                self._contenu,
                self.bibliotheque,
            ),
        }

        for page in self._pages.values():
            page.grid(row=0, column=0, sticky="nsew")
            page.grid_remove()

    def _construire_barre_etat(self) -> None:
        self._barre_etat = ctk.CTkFrame(
            self,
            height=32,
            corner_radius=0,
            fg_color=("gray88", "gray15"),
        )
        self._barre_etat.grid(
            row=1, column=0, columnspan=2, sticky="ew"
        )
        self._barre_etat.grid_columnconfigure(0, weight=1)
        self._barre_etat.grid_propagate(False)

        self._label_statut = ctk.CTkLabel(
            self._barre_etat,
            text="",
            anchor="w",
            font=ctk.CTkFont(size=12),
        )
        self._label_statut.grid(
            row=0, column=0, sticky="ew", padx=14, pady=6
        )

    def _afficher_page(self, nom: str) -> None:
        if nom not in self._pages:
            return

        for cle, page in self._pages.items():
            if cle == nom:
                page.grid(row=0, column=0, sticky="nsew")
                page.tkraise()
            else:
                page.grid_remove()

        for cle, bouton in self._boutons_navigation.items():
            if cle == nom:
                bouton.configure(fg_color=("gray78", "gray28"))
            else:
                bouton.configure(fg_color="transparent")

        self._pages[nom].rafraichir()

    def rafraichir_tout(self) -> None:
        for page in self._pages.values():
            page.rafraichir()

    def _apres_mutation(self, message: str) -> None:
        self.rafraichir_tout()
        self._definir_statut(message)

    def _definir_statut(self, message: str, erreur: bool = False) -> None:
        self._label_statut.configure(
            text=message,
            text_color="#d9534f" if erreur else ("gray15", "gray85"),
        )

    def _sauvegarder(self) -> None:
        try:
            self.bibliotheque.sauvegarder()
        except ErreurBibliotheque as exc:
            self._definir_statut(str(exc), erreur=True)
            messagebox.showerror(
                "Erreur de sauvegarde",
                str(exc),
                parent=self,
            )
            return

        self._definir_statut("Données sauvegardées avec succès.")

    def _creer_sauvegarde(self) -> None:
        try:
            copies = self.bibliotheque.creer_sauvegarde()
        except ErreurBibliotheque as exc:
            self._definir_statut(str(exc), erreur=True)
            messagebox.showerror(
                "Erreur de sauvegarde",
                str(exc),
                parent=self,
            )
            return

        if copies:
            self._definir_statut(
                f"Sauvegarde créée : {len(copies)} fichier"
                f"{'s' if len(copies) > 1 else ''} .backup."
            )
        else:
            self._definir_statut("Aucun fichier de données à sauvegarder.")

    def _changer_apparence(self, choix: str) -> None:
        correspondance = {
            "Système": "system",
            "Clair": "light",
            "Sombre": "dark",
        }
        ctk.set_appearance_mode(correspondance.get(choix, "system"))

    def _afficher_erreur_chargement(self) -> None:
        if self._erreur_chargement is None:
            return
        self._definir_statut(self._erreur_chargement, erreur=True)
        messagebox.showerror(
            "Erreur de chargement",
            self._erreur_chargement,
            parent=self,
        )

    def _fermer(self) -> None:
        try:
            self.bibliotheque.sauvegarder()
        except ErreurBibliotheque as exc:
            quitter = messagebox.askyesno(
                "Erreur de sauvegarde",
                f"Impossible de sauvegarder les données :\n{exc}\n\n"
                "Quitter quand même ?",
                parent=self,
            )
            if not quitter:
                return

        self.destroy()
