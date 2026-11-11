import customtkinter as ctk


def main():
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Application de test")
    app.geometry("500x300")

    label = ctk.CTkLabel(
        app,
        text="Bienvenue dans l'application de test CustomTkinter !",
        font=ctk.CTkFont(size=20, weight="bold"),
    )
    label.pack(expand=True)

    app.mainloop()


if __name__ == "__main__":
    main()
