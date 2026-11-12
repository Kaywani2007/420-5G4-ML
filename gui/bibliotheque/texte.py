from __future__ import annotations

import unicodedata

_REMPLACEMENTS_LIGATURES = str.maketrans(
    {
        "œ": "oe",
        "Œ": "OE",
        "æ": "ae",
        "Æ": "AE",
    }
)


def normaliser_texte(texte: str) -> str:
    decompose = unicodedata.normalize(
        "NFKD",
        (texte or "").translate(_REMPLACEMENTS_LIGATURES),
    )
    sans_accents = "".join(
        caractere
        for caractere in decompose
        if not unicodedata.combining(caractere)
    )
    return sans_accents.casefold().strip()
