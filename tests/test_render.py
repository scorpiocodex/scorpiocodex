"""Every renderer produces a valid, safe SVG from sample data (no network)."""

import unittest

from profilegen import activity, build, validate
from tests.sample_data import sample_data


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.profile = build.load_profile()
        self.files = build.render_all(self.profile, sample_data())

    def test_every_image_passes_validation(self):
        for name, text in self.files.items():
            with self.subTest(name):
                self.assertEqual(validate.problems(text, name), [])

    def test_one_image_per_project_plus_the_shared_ones(self):
        expected = {
            "banner.svg",
            "stats.svg",
            "languages.svg",
            "heatmap.svg",
            "skills.svg",
            "btn-portfolio.svg",
            "btn-linkedin.svg",
            "btn-email.svg",
        }
        expected |= {f"project-{p['repo'].lower()}.svg" for p in self.profile["projects"]}
        self.assertEqual(set(self.files), expected)

    def test_social_cards_exist_for_every_project_and_are_valid(self):
        cards = build.render_social(self.profile)
        self.assertEqual(set(cards), {f"{p['repo'].lower()}.svg" for p in self.profile["projects"]})
        for name, text in cards.items():
            with self.subTest(name):
                self.assertEqual(validate.problems(text, f"social/{name}"), [])
                self.assertIn('viewBox="0 0 1280 640"', text)

    def test_social_cards_show_only_facts_from_the_data_file(self):
        for project in self.profile["projects"]:
            text = build.render_social(self.profile)[f"{project['repo'].lower()}.svg"]
            self.assertIn(project["name"], text)
            self.assertIn(project["short"], text)

    def test_rendering_is_deterministic(self):
        again = build.render_all(self.profile, sample_data())
        self.assertEqual(self.files, again)

    def test_top_languages_adds_up_and_groups_the_tail(self):
        langs = activity.top_languages({"A": 50, "B": 30, "C": 10, "D": 5, "E": 3, "F": 1, "G": 1}, limit=5)
        self.assertEqual([n for n, _ in langs][:5], ["A", "B", "C", "D", "E"])
        self.assertEqual(langs[-1][0], "Other")
        self.assertAlmostEqual(sum(p for _, p in langs), 100.0, places=6)

    def test_missing_languages_does_not_crash(self):
        data = sample_data()
        data["languages"] = {}
        self.assertEqual(validate.problems(activity.languages_card(data), "languages"), [])


class ValidatorTests(unittest.TestCase):
    """The validator has to actually reject what it claims to reject."""

    def wrap(self, inner: str, style: str = "") -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><title>t</title><desc>d</desc>'
            f"<style>{style}@media (prefers-reduced-motion: reduce){{*{{animation:none}}}}</style>{inner}</svg>"
        )

    def test_accepts_a_clean_image(self):
        self.assertEqual(validate.problems(self.wrap("<rect width='1' height='1'/>")), [])

    def test_rejects_active_or_external_content(self):
        for bad in (
            "<script>alert(1)</script>",
            "<foreignObject/>",
            "<image href='https://example.com/x.png'/>",
            "<a href='https://example.com'><rect/></a>",
            "<rect onclick='x()'/>",
            "<rect style='fill:url(https://example.com/x)'/>",
        ):
            with self.subTest(bad):
                self.assertNotEqual(validate.problems(self.wrap(bad)), [])

    def test_rejects_content_hidden_outside_keyframes(self):
        self.assertTrue(validate.problems(self.wrap("<rect opacity='0'/>")))
        self.assertTrue(validate.problems(self.wrap("<rect/>", ".x{opacity:0}")))

    def test_allows_hiding_inside_keyframes_and_zero_stop_opacity(self):
        style = "@keyframes a{from{opacity:0}to{opacity:1}}"
        self.assertEqual(validate.problems(self.wrap("<stop stop-opacity='0'/>", style)), [])

    def test_requires_a_reduced_motion_rule_for_animated_images(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg"><title>t</title><desc>d</desc>'
            "<style>@keyframes a{from{opacity:.5}to{opacity:1}}</style></svg>"
        )
        self.assertTrue(validate.problems(svg))

    def test_rejects_oversized_and_malformed(self):
        self.assertTrue(validate.problems("<svg"))
        self.assertTrue(validate.problems(self.wrap("<!-- " + "x" * validate.MAX_BYTES + " -->")))


if __name__ == "__main__":
    unittest.main()
