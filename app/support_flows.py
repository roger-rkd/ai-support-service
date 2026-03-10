"""Deterministic short support flows for common requests."""

from typing import Optional


def is_postcode_memory_question(question: str) -> bool:
    """Detect short memory questions about prior postcodes."""
    normalized = question.casefold()
    return (
        ("remember" in normalized or "first" in normalized or "previous" in normalized)
        and ("postcode" in normalized or "post code" in normalized)
    )


def build_postcode_memory_answer(postcode: Optional[str]) -> str:
    """Return a concise answer about remembered postcodes for this session."""
    if postcode:
        return (
            f"Yes. The first postcode you shared in this chat was **{postcode}**.\n"
            "- Send any postcode and I will return a **Google Maps** link for nearby GP practices."
        )

    return (
        "I do not have a postcode saved in this current chat yet.\n"
        "- Send a **postcode** and I will return a **Google Maps** link for nearby GP practices."
    )


def is_appointment_request(question: str) -> bool:
    """Detect booking and appointment support requests."""
    normalized = question.casefold()
    return (
        "appointment" in normalized
        or "book" in normalized
        or "booking" in normalized
    ) and ("gp" in normalized or "doctor" in normalized or "nhs" in normalized or "help" in normalized)


def build_appointment_answer(postcode: Optional[str]) -> str:
    """Return a concise appointment assistance response."""
    postcode_line = (
        f"- I can also find your nearest **GP** using **{postcode}**.\n"
        if postcode
        else "- I can also help find your nearest **GP** if you send your **postcode**.\n"
    )
    return (
        "I can help with **appointment assistance**.\n"
        f"{postcode_line}"
        "- Phone your **GP surgery** or use their online booking service.\n"
        "- If it is urgent and you are unsure where to go, call **111**."
    )
