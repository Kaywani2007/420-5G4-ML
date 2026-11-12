from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import customtkinter as ctk
from tkinter import ttk


class TableauDonnees(ctk.CTkFrame):
    def __init__(
        self,
        master: Any,
        colonnes: Sequence[tuple[str, str, int]],
        hauteur: int = 12,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._elements: dict[str, Any] = {}
        identifiants = [cle for cle, _, _ in colonnes]
        self.arbres = ttk.Treeview(
            self,
            columns=identifiants,
            show="headings",
            selectmode="browse",
            height=hauteur,
        )

        for cle, titre, largeur in colonnes:
            self.arbres.heading(cle, text=titre)
            self.arbres.column(
                cle,
                width=largeur,
                minwidth=70,
                anchor="w",
                stretch=True,
            )

        self.arbres.grid(row=0, column=0, sticky="nsew")
        self.barre = ttk.Scrollbar(
            self, orient="vertical", command=self.arbres.yview
        )
        self.barre.grid(row=0, column=1, sticky="ns")
        self.arbres.configure(yscrollcommand=self.barre.set)
        self.arbres.tag_configure("emprunte", foreground="#c46a2d")

    def remplir(
        self,
        elements: Sequence[Any],
        formateur: Callable[[Any], Sequence[str]],
        tag_fonction: Callable[[Any], bool] | None = None,
    ) -> None:
        self.vider()
        for element in elements:
            tags = ()
            if tag_fonction is not None and tag_fonction(element):
                tags = ("emprunte",)
            iid = self.arbres.insert(
                "",
                "end",
                values=tuple(formateur(element)),
                tags=tags,
            )
            self._elements[iid] = element

    def vider(self) -> None:
        for iid in self.arbres.get_children():
            self.arbres.delete(iid)
        self._elements.clear()

    def selection(self) -> Any | None:
        selection = self.arbres.selection()
        if not selection:
            return None
        return self._elements.get(selection[0])


class CarteStatistique(ctk.CTkFrame):
    def __init__(
        self,
        master: Any,
        titre: str,
        valeur: int = 0,
        couleur: str | tuple[str, str] = "#1f6aa5",
    ) -> None:
        super().__init__(master, corner_radius=14)
        self.grid_columnconfigure(1, weight=1)

        self._indicateur = ctk.CTkFrame(
            self, width=8, height=64, corner_radius=4, fg_color=couleur
        )
        self._indicateur.grid(row=0, column=0, rowspan=2, padx=(14, 10), pady=18)

        self._titre = ctk.CTkLabel(
            self,
            text=titre,
            anchor="w",
            font=ctk.CTkFont(size=13),
        )
        self._titre.grid(row=0, column=1, sticky="ew", padx=(0, 18), pady=(18, 0))

        self._valeur = ctk.CTkLabel(
            self,
            text=str(valeur),
            anchor="w",
            font=ctk.CTkFont(size=30, weight="bold"),
        )
        self._valeur.grid(row=1, column=1, sticky="ew", padx=(0, 18), pady=(0, 18))

    def definir_valeur(self, valeur: int) -> None:
        self._valeur.configure(text=str(valeur))
