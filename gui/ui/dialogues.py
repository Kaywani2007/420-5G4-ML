from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import customtkinter as ctk

from bibliotheque.service import Bibliotheque

Validateur = Callable[[dict[str, str]], None]


class DialogueFormulaire(ctk.CTkToplevel):
    def __init__(
        self,
        parent: Any,
        titre: str,
        champs: Sequence[tuple[str, str]],
        texte_valider: str = "Valider",
        validateur: Validateur | None = None,
    ) -> None:
        super().__init__(parent)
        self.title(titre)
        self.resizable(False, False)

        fenetre_parent = parent.winfo_toplevel()
        self.transient(fenetre_parent)

        self.resultat: dict[str, str] | None = None
        self._validateur = validateur
        self._entries: dict[str, ctk.CTkEntry] = {}

        self.protocol("WM_DELETE_WINDOW", self._annuler)
        self.bind("<Escape>", lambda _event: self._annuler())
        self.bind("<Return>", lambda _event: self._valider())

        ctk.CTkLabel(
            self,
            text=titre,
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=24, pady=(22, 14))

        for cle, libelle in champs:
            cadre = ctk.CTkFrame(self, fg_color="transparent")
            cadre.pack(fill="x", padx=24, pady=(0, 10))

            ctk.CTkLabel(
                cadre,
                text=libelle,
                anchor="w",
                font=ctk.CTkFont(size=13),
            ).pack(fill="x", pady=(0, 4))

            entry = ctk.CTkEntry(cadre, height=36)
            entry.pack(fill="x")
            self._entries[cle] = entry

        self._erreur = ctk.CTkLabel(
            self,
            text="",
            text_color="#d9534f",
            justify="left",
            anchor="w",
            wraplength=410,
        )
        self._erreur.pack(fill="x", padx=24, pady=(0, 8))

        boutons = ctk.CTkFrame(self, fg_color="transparent")
        boutons.pack(fill="x", padx=24, pady=(0, 20))
        boutons.grid_columnconfigure(0, weight=1)
        boutons.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            boutons,
            text="Annuler",
            fg_color="transparent",
            border_width=1,
            command=self._annuler,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            boutons,
            text=texte_valider,
            command=self._valider,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        largeur = 470
        hauteur = 225 + len(champs) * 76
        self.update_idletasks()
        self.geometry(f"{largeur}x{hauteur}")
        self._centrer(fenetre_parent, largeur, hauteur)

        self.after(60, self._finaliser)

    def _finaliser(self) -> None:
        try:
            self.grab_set()
        except Exception:
            pass
        self.focus_force()
        if self._entries:
            next(iter(self._entries.values())).focus_set()

    def _centrer(self, parent: Any, largeur: int, hauteur: int) -> None:
        try:
            x = parent.winfo_rootx() + max((parent.winfo_width() - largeur) // 2, 0)
            y = parent.winfo_rooty() + max((parent.winfo_height() - hauteur) // 2, 0)
        except Exception:
            x = max((self.winfo_screenwidth() - largeur) // 2, 0)
            y = max((self.winfo_screenheight() - hauteur) // 2, 0)
        self.geometry(f"{largeur}x{hauteur}+{x}+{y}")

    def _valider(self) -> None:
        donnees = {
            cle: entry.get().strip() for cle, entry in self._entries.items()
        }

        try:
            if self._validateur is not None:
                self._validateur(donnees)
        except Exception as exc:
            message = str(exc) or "Les informations saisies sont invalides."
            self._erreur.configure(text=message)
            return

        self.resultat = donnees
        self.destroy()

    def _annuler(self) -> None:
        self.resultat = None
        self.destroy()


def demander_formulaire(
    parent: Any,
    titre: str,
    champs: Sequence[tuple[str, str]],
    texte_valider: str = "Valider",
    validateur: Validateur | None = None,
) -> dict[str, str] | None:
    dialogue = DialogueFormulaire(
        parent,
        titre,
        champs,
        texte_valider=texte_valider,
        validateur=validateur,
    )
    parent.wait_window(dialogue)
    return dialogue.resultat


def demander_ajout_livre(
    parent: Any, bibliotheque: Bibliotheque
) -> dict[str, str] | None:
    def valider(donnees: dict[str, str]) -> None:
        bibliotheque.verifier_ajout_livre(
            donnees["titre"],
            donnees["auteur"],
            donnees["isbn"],
        )

    return demander_formulaire(
        parent,
        "Ajouter un livre",
        [
            ("titre", "Titre"),
            ("auteur", "Auteur"),
            ("isbn", "ISBN"),
        ],
        texte_valider="Ajouter",
        validateur=valider,
    )


def demander_ajout_utilisateur(
    parent: Any, bibliotheque: Bibliotheque
) -> dict[str, str] | None:
    def valider(donnees: dict[str, str]) -> None:
        bibliotheque.verifier_ajout_utilisateur(
            donnees["nom"],
            donnees["identifiant"],
        )

    return demander_formulaire(
        parent,
        "Ajouter un utilisateur",
        [
            ("nom", "Nom"),
            ("identifiant", "ID utilisateur"),
        ],
        texte_valider="Ajouter",
        validateur=valider,
    )
