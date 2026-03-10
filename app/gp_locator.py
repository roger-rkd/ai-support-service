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


def build_gp_locator_answer(postcode: Optional[str]) -> str:
    """Return a deterministic response for nearby GP requests."""
    if not postcode:
        return (
            "I can help with **GP location assistance**.\n"
            "- Please send your **postcode** so I can generate a **Google Maps** link for nearby GP practices.\n"
            "- For example, you can reply with **SW1A 1AA**."
        )

    maps_query = quote_plus(f"GP practice near {postcode}")
    maps_link = f"https://www.google.com/maps/search/?api=1&query={maps_query}"
    return (
        "I can help with **GP location assistance**.\n"
        f"- I found the postcode **{postcode}** in your message.\n"
        f"- Open this **Google Maps** search for nearby GP practices: {maps_link}\n"
        "- If you want, I can also help with **appointment assistance** after you choose a surgery."
    )
