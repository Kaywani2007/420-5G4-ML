import customtkinter as ctk

from ui.fenetre_principale import FenetrePrincipale


def main() -> None:
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    application = FenetrePrincipale()
    application.mainloop()


if __name__ == "__main__":
    main()
