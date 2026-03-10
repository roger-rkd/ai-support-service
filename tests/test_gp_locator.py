import unittest

from app.gp_locator import (
    build_gp_locator_answer,
    extract_uk_postcode,
    is_gp_locator_request,
    is_postcode_only_message,
)
from app.session_memory import append_session_message, get_session_state


class GpLocatorTests(unittest.TestCase):
    def test_detects_gp_locator_request(self):
        self.assertTrue(is_gp_locator_request("Find my nearest GP practice"))
        self.assertFalse(is_gp_locator_request("What are home remedies for a cold?"))

    def test_extracts_uk_postcode(self):
        self.assertEqual(
            extract_uk_postcode("Find a GP near sw1a1aa"),
            "SW1A 1AA",
        )

    def test_requests_postcode_when_missing(self):
        answer = build_gp_locator_answer(None)
        self.assertIn("postcode", answer.lower())
        self.assertNotIn("google.com/maps", answer)

    def test_detects_postcode_only_message(self):
        self.assertTrue(is_postcode_only_message("g3 8qp"))
        self.assertFalse(is_postcode_only_message("find a GP near g3 8qp"))

    def test_returns_google_maps_link_when_postcode_present(self):
        answer = build_gp_locator_answer("SW1A 1AA")
        self.assertIn("SW1A 1AA", answer)
        self.assertIn("google.com/maps/search/", answer)
        self.assertIn("GP+practice+near+SW1A+1AA", answer)

    def test_session_state_tracks_pending_postcode_follow_up(self):
        session_state = get_session_state("test-session")
        session_state["pending_postcode_for_gp"] = True
        postcode = extract_uk_postcode("g3 8qp")

        self.assertEqual(postcode, "G3 8QP")
        answer = build_gp_locator_answer(postcode)

        self.assertIn("google.com/maps/search/", answer)
        self.assertIn("G3 8QP", answer)
        append_session_message(session_state, "user", "g3 8qp")
        append_session_message(session_state, "assistant", answer)
        self.assertEqual(len(session_state["messages"]), 2)


if __name__ == "__main__":
    unittest.main()
