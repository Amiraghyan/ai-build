# ────────────────────────────────────────────────────────────────
# File: anonymizer_api/anonymizer.py (v3 – couverture PII étendue)
# Description: Détection & masquage exhaustifs de PII françaises
# ----------------------------------------------------------------
"""Anonymizer v3

• Approche hybride règles + spaCy NER + phonenumbers
• Validation algorithmique (IBAN mod 97, Luhn cartes, clé NIR)
• Nouvelles entités : emails complexes, IBAN/RIB, dates (alpha), permis,
  immatriculation véhicule, etc.
• Une seule reconstruction du texte (rapide, O(n))
"""
from __future__ import annotations

import regex                      # regex plus rapide que re & overlap
import phonenumbers as _pn        # détection + validation téléphones
from dateutil.parser import parse as _dt_parse
from functools import lru_cache
from typing import List, NamedTuple, Sequence
import unicodedata

import spacy

__all__ = ["anonymize_all", "anonymize_all_many"]

# ---------------------------------------------------------------------------
# 1) Modèle spaCy (PERSON) ---------------------------------------------------
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_spacy():
    nlp = spacy.load(
        "fr_core_news_sm",
        disable=["tagger", "parser", "lemmatizer", "attribute_ruler"],
    )
    nlp.select_pipes(enable=["ner"])
    return nlp

_nlp = _load_spacy()

# ---------------------------------------------------------------------------
# 2) Fonctions auxiliaires ---------------------------------------------------
# ---------------------------------------------------------------------------

def _strip(acc: str) -> str:
    """Remove spaces/dashes from IDs (ex : IBAN, carte)."""
    return regex.sub(r"[\s-]", "", acc)


# ——— Validation IBAN --------------------------------------------------------
_alpha_to_num = {chr(i + 55): str(i) for i in range(10, 36)}  # A→10, B→11…

def _iban_to_numeric(iban: str) -> str:
    return "".join(_alpha_to_num.get(ch, ch) for ch in iban)

def _is_valid_iban(iban: str) -> bool:
    raw = _strip(iban).upper()
    if not raw.startswith("FR") or len(raw) != 27:
        return False
    # réarrangement
    rearr = raw[4:] + raw[:4]
    num = int(_iban_to_numeric(rearr))
    return num % 97 == 1


# ——— Validation Luhn pour cartes -------------------------------------------

def _is_valid_luhn(number: str) -> bool:
    digits = [int(d) for d in number if d.isdigit()][::-1]
    check_sum = 0
    for i, d in enumerate(digits):
        if i % 2:
            d *= 2
            if d > 9:
                d -= 9
        check_sum += d
    return check_sum % 10 == 0


# ——— Validation clé NIR -----------------------------------------------------

def _is_valid_nir(nir: str) -> bool:
    num = _strip(nir)
    if len(num) != 15 or not num.isdigit():
        return False
    key = int(num[-2:])
    n = int(num[:-2])
    return (97 - n % 97) == key


# ---------------------------------------------------------------------------
# 3) Patterns regex + fonctions de masquage ----------------------------------
# ---------------------------------------------------------------------------

# Emails complets
_email_pat = regex.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# IBAN FR 27 car / RIB traditionnel
_iban_pat = regex.compile(r"FR[0-9A-Za-z]{2}(?:[\s]?[0-9A-Za-z]{4}){5}[0-9A-Za-z]{1}")
_rib_pat = regex.compile(r"\b\d{5}\s?\d{5}\s?\d{11}\s?\d{2}\b")

# Cartes bancaires 13–16 chiffres (espaces ou tirets autorisés)
_card_pat = regex.compile(r"(?:\d[\s-]?){13,16}")

# Dates JJ/MM/AAAA
_date_num_pat = regex.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b")
# Dates texte (12 mars 1990)
_months = "janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre"
_date_alpha_pat = regex.compile(rf"\b\d{{1,2}} (?:{_months}) \d{{4}}\b", flags=regex.IGNORECASE)

# NIR
_nir_pat = regex.compile(r"\b[12]\d{2}\d{2}\d{2}\d{3}\d{3}\d{2}\b")

# Passeport FR
_passport_pat = regex.compile(r"\b\d{2}[A-Z]{2}\d{5}\b", flags=regex.IGNORECASE)
# Permis : 12 chiffres consécutifs
_permis_pat = regex.compile(r"\b\d{12}\b")
# Immatriculation véhicule AA-123-AA
_plate_pat = regex.compile(r"\b[A-Z]{2}-\d{3}-[A-Z]{2}\b", flags=regex.IGNORECASE)

# Adresse heuristique
_addr_pat = regex.compile(
    r"\b\d{1,4}\s+[^,\n]{2,80},?\s+\d{5}\s+[A-ZÉÈÀÂÊÎÔÛÇ][a-zà-ÿ\-\s]{2,50}\b",
    flags=regex.VERSION1 | regex.IGNORECASE,
)

# ----------------- Masques --------------------------------------------------

def _mask_generic(label: str) -> str:
    return label

def _mask_email(x: str) -> str:
    local, domain = x.split("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def _mask_card(x: str) -> str:
    digits = _strip(x)
    return "*" * (len(digits) - 4) + digits[-4:]


def _mask_phone(x: str) -> str:
    digits = _strip(x)
    return "X" * (len(digits) - 2) + digits[-2:]


def _mask_iban(x: str) -> str:
    tail = _strip(x)[-4:]
    return "FR************" + tail


def _mask_rib(x: str) -> str:
    return "************" + x[-4:]


def _mask_date(x: str) -> str:
    try:
        year = _dt_parse(x, dayfirst=True, fuzzy=True).year
        return f"XX/XX/{year}"
    except Exception:
        return "DATE"


def _mask_nir(x: str) -> str:
    return "***********" + x[-4:]


def _mask_passport(x: str) -> str:
    return x[:2] + "*" * (len(x) - 4) + x[-2:]


def _mask_license(x: str) -> str:
    return "PERMIS********"

# Mapping pattern → mask
_PATTERNS: Sequence[tuple[regex.Pattern, callable[[str], str], callable[[str], bool] | None]] = (
    (_addr_pat, lambda _: "ADRESSE", None),
    (_iban_pat, _mask_iban, _is_valid_iban),
    (_rib_pat, _mask_rib, None),
    (_date_num_pat, _mask_date, None),
    (_date_alpha_pat, _mask_date, None),
    (_passport_pat, _mask_passport, None),
    (_permis_pat, _mask_license, None),
    (_plate_pat, lambda _: "IMMATRICULATION", None),
    (_card_pat, _mask_card, _is_valid_luhn),
    (_email_pat, _mask_email, None),
    (_nir_pat, _mask_nir, _is_valid_nir),
)

# ---------------------------------------------------------------------------
# 4) Collecte des remplacements ---------------------------------------------
# ---------------------------------------------------------------------------

class _Repl(NamedTuple):
    start: int
    end: int
    repl: str


def _gather_regex(text: str) -> list[_Repl]:
    out: list[_Repl] = []
    for pat, masker, validator in _PATTERNS:
        for m in pat.finditer(text):
            val_ok = validator(m.group(0)) if validator else True
            if val_ok:
                out.append(_Repl(m.start(), m.end(), masker(m.group(0))))
    return out


def _gather_phones(text: str) -> list[_Repl]:
    out: list[_Repl] = []
    for match in _pn.PhoneNumberMatcher(text, "FR"):
        num = match.number
        if not _pn.is_possible_number(num):
            continue
        raw = text[match.start:match.end]
        out.append(_Repl(match.start, match.end, _mask_phone(raw)))
    return out


def _gather_person(doc: "spacy.tokens.Doc") -> list[_Repl]:
    out: list[_Repl] = []
    for ent in doc.ents:
        if ent.label_ == "PER":
            masked = ent.text[0] + "*" * (len(ent.text) - 1) if len(ent.text) > 1 else "*"
            out.append(_Repl(ent.start_char, ent.end_char, masked))
    return out


# ---------------------------------------------------------------------------
# 5) Application des remplacements ------------------------------------------
# ---------------------------------------------------------------------------

def _apply(text: str, repls: list[_Repl]) -> str:
    if not repls:
        return text
    repls.sort(key=lambda r: r.start)
    out, cursor = [], 0
    for r in repls:
        if r.start < cursor:
            continue  # chevauchement – ignore plus tardif
        out.append(text[cursor : r.start])
        out.append(r.repl)
        cursor = r.end
    out.append(text[cursor:])
    return "".join(out)


# ---------------------------------------------------------------------------
# 6) API publiques -----------------------------------------------------------
# ---------------------------------------------------------------------------

def anonymize_all(text: str) -> str:
    repls = _gather_regex(text)
    repls.extend(_gather_phones(text))
    doc = _nlp(text)
    repls.extend(_gather_person(doc))
    return _apply(text, repls)


def anonymize_all_many(texts: List[str]) -> List[str]:
    regex_batches = [_gather_regex(t) for t in texts]
    phone_batches = [_gather_phones(t) for t in texts]
    docs = _nlp.pipe(texts, batch_size=16)
    results: list[str] = []
    for txt, reg_r, ph_r, doc in zip(texts, regex_batches, phone_batches, docs, strict=True):
        repls = reg_r + ph_r + _gather_person(doc)
        results.append(_apply(txt, repls))
    return results
