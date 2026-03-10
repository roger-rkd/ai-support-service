import unittest

from app.gp_locator import (
    build_gp_locator_answer,
    extract_uk_postcode,
    is_gp_locator_request,
)


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

    def test_returns_google_maps_link_when_postcode_present(self):
        answer = build_gp_locator_answer("SW1A 1AA")
        self.assertIn("SW1A 1AA", answer)
        self.assertIn("google.com/maps/search/", answer)
        self.assertIn("GP+practice+near+SW1A+1AA", answer)


if __name__ == "__main__":
    unittest.main()
