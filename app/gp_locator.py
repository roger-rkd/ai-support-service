"""Helpers for postcode-aware GP locator responses."""

from typing import Optional
import re
from urllib.parse import quote_plus


UK_POSTCODE_PATTERN = re.compile(
    r"\b([A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2})\b",
    re.IGNORECASE,
)


def extract_uk_postcode(question: str) -> Optional[str]:
    """Extract a UK postcode from the user's question."""
    match = UK_POSTCODE_PATTERN.search(question)
    if not match:
        return None
    postcode = re.sub(r"\s+", "", match.group(1).upper())
    if len(postcode) > 3:
        postcode = f"{postcode[:-3]} {postcode[-3:]}"
    return postcode.strip()


def is_gp_locator_request(question: str) -> bool:
    """Detect whether the user is asking to find a nearby GP."""
    normalized = question.casefold()
    gp_terms = ("gp", "doctor", "surgery", "practice")
    location_terms = ("nearest", "near me", "nearby", "find", "locate", "closest")
    return any(term in normalized for term in gp_terms) and any(
        term in normalized for term in location_terms
    )


def is_postcode_only_message(question: str) -> bool:
    """Detect whether the user's message is effectively just a postcode."""
    postcode = extract_uk_postcode(question)
    if not postcode:
        return False

    normalized = re.sub(r"[^A-Z0-9]", "", question.upper())
    postcode_compact = re.sub(r"[^A-Z0-9]", "", postcode)
    return normalized == postcode_compact


def build_gp_locator_answer(postcode: Optional[str]) -> str:
    """Return a deterministic response for nearby GP requests."""
    if not postcode:
        return (
            "Send your **postcode**.\n"
            "- I will return a **Google Maps** link for nearby GP practices.\n"
            "- Example: **SW1A 1AA**."
        )

    maps_query = quote_plus(f"GP practice near {postcode}")
    maps_link = f"https://www.google.com/maps/search/?api=1&query={maps_query}"
    return (
        f"Nearest GP search for **{postcode}**:\n"
        f"- **Click here to find your nearest GP:** {maps_link}\n"
        "- Alternatively, call **NHS 24 on 111** to book your appointment."
    )
