"""The committed images and README: the checks that matter before anything is published."""

import json
import re
import struct
import unittest
from pathlib import Path

from profilegen import build, validate
from tests.sample_data import sample_data

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
PROFILE = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))

STATUS = "I'm looking for a Python backend or full-stack developer role."


class CommittedImagesTests(unittest.TestCase):
    def test_every_committed_image_passes_validation(self):
        files = sorted((ROOT / "assets" / "generated").glob("*.svg"))
        self.assertGreater(len(files), 0, "no generated images; run `python3 build.py`")
        for path in files:
            with self.subTest(path.name):
                self.assertEqual(validate.problems(path.read_text(encoding="utf-8"), path.name), [])

    def test_every_expected_image_is_committed(self):
        expected = set(build.render_all(PROFILE, sample_data()))
        present = {p.name for p in (ROOT / "assets" / "generated").glob("*.svg")}
        self.assertEqual(expected - present, set())


class SocialPreviewTests(unittest.TestCase):
    """The repository preview cards: SVG source plus the PNG exported for GitHub."""

    def test_every_card_has_valid_source_and_a_png_within_githubs_limits(self):
        for project in PROFILE["projects"]:
            name = project["repo"].lower()
            svg = ROOT / "assets" / "social" / f"{name}.svg"
            png = ROOT / "assets" / "social" / f"{name}.png"
            with self.subTest(name):
                self.assertTrue(svg.is_file() and png.is_file(), "missing .svg or .png; export it from the SVG")
                self.assertEqual(validate.problems(svg.read_text(encoding="utf-8"), svg.name), [])
                data = png.read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                width, height = struct.unpack(">II", data[16:24])
                self.assertEqual((width, height), (1280, 640))
                self.assertLess(len(data), 1_000_000, "GitHub rejects social previews of 1 MB or more")


class ReadmeTests(unittest.TestCase):
    def test_every_image_has_alt_text_and_an_existing_file(self):
        imgs = re.findall(r"<img\b[^>]*>", README)
        self.assertGreater(len(imgs), 5)
        for tag in imgs:
            alt = re.search(r'alt="([^"]+)"', tag)
            src = re.search(r'src="([^"]+)"', tag)
            with self.subTest(tag[:70]):
                self.assertTrue(alt and alt.group(1).strip(), "missing alt text")
                self.assertTrue(src)
                self.assertTrue((ROOT / src.group(1)).is_file(), f"missing file {src.group(1)}")

    def test_every_generated_image_is_used_by_the_readme(self):
        for path in (ROOT / "assets" / "generated").glob("*.svg"):
            with self.subTest(path.name):
                self.assertIn(f"assets/generated/{path.name}", README)

    def test_no_active_html(self):
        for banned in ("<script", "<style", "<iframe", "javascript:"):
            self.assertNotIn(banned, README.lower())

    def test_contact_links_match_the_data_file(self):
        links = PROFILE["links"]
        self.assertIn(links["portfolio"], README)
        self.assertIn(links["linkedin"], README)
        self.assertIn(f"mailto:{links['email']}", README)

    def test_headline_facts_are_in_the_text_not_only_in_images(self):
        for fact in (PROFILE["role"], PROFILE["location"], STATUS):
            self.assertIn(fact, README)

    def test_project_facts_match_the_data_file(self):
        plain = README.replace("`", "")
        for project in PROFILE["projects"]:
            with self.subTest(project["name"]):
                self.assertIn(project["tagline"], plain)
                self.assertIn(f"github.com/scorpiocodex/{project['repo']}", README)
                for bullet in project["bullets"]:
                    self.assertIn(bullet.format(**PROFILE["bakeriq_facts"]), plain)

    def test_stack_text_matches_the_data_file(self):
        for group in PROFILE["stack"]:
            with self.subTest(group["area"]):
                for item in group["items"]:
                    self.assertIn(item, README)

    def test_background_is_present(self):
        for line in PROFILE["background"]:
            self.assertIn(line, README)


if __name__ == "__main__":
    unittest.main()
