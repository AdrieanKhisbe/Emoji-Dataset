import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests
from PIL import Image

import emoji_dataset

UNICODE = """# emoji-test.txt
# Version: 17.0
1F600 ; fully-qualified # 😀 E1.0 grinning face
1F44B 1F3FB ; fully-qualified # 👋🏻 E1.0 waving hand: light skin tone
263A ; unqualified # ☺ E0.6 smiling face
"""


def png(color):
    output = io.BytesIO()
    Image.new("RGBA", (2, 2), color).save(output, format="PNG")
    return output.getvalue()


def response(content, status=200, headers=None):
    result = requests.Response()
    result.status_code = status
    result._content = content if isinstance(content, bytes) else json.dumps(content).encode()
    result.headers.update(headers or {})
    return result


class Sources:
    def __init__(self):
        self.unicode = UNICODE
        self.images = {}
        self.catalogs = {}
        self.releases = {}

    def vendor(self, slug, color, version="v1", date=1):
        source = f"source/{slug}/123/grinning-face_1f600.png"
        self.images[f"https://em-content.zobj.net/{source}"] = png(color)
        self.releases[slug] = [{"slug": version, "title": version, "date": date}]
        self.catalogs[slug] = {"items": [{"images": [
            {"slug": "grinning-face", "image": {"source": source}, "status": "CHANGED"}
        ]}], "statuses": ["CHANGED"]}
        return self.images[f"https://em-content.zobj.net/{source}"]

    def get(self, url, **kwargs):
        if url == emoji_dataset.UNICODE_URL:
            return response(self.unicode.encode())
        item = self.images[url]
        return item if isinstance(item, requests.Response) else response(item)

    def post(self, url, *, json, **kwargs):
        assert url == "https://emojipedia.org/api/graphql"
        slug = json["variables"]["slug"]
        if json["operationName"] == "VendorReleases":
            return response({"data": {"vendorHistoric_v1": self.releases[slug]}})
        return response({"data": {"vendorHistoricEmoji_v1": self.catalogs[slug]}})


def run(output, sources, *vendors):
    args = ["--output", str(output), "--cache-dir", str(output.parent / "cache"), "--request-delay", "0"]
    for vendor in vendors:
        args.extend(["--vendor", vendor])
    with patch.object(requests.Session, "get", side_effect=sources.get), \
         patch.object(requests.Session, "post", side_effect=sources.post), \
         contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        return emoji_dataset.main(args)


class RegenerateTests(unittest.TestCase):
    def test_legacy_shared_path_is_split_without_overwriting_retained_artwork(self):
        sources = Sources()
        sources.vendor("apple", "red")
        sources.unicode = "# Version: 17.0\n0023 FE0F 20E3 ; fully-qualified # #️⃣ E0.6 keycap: #\n002A FE0F 20E3 ; fully-qualified # *️⃣ E2.0 keycap: *\n"
        source = "source/apple/123/keycap_23-fe0f-20e3.png"
        sources.catalogs["apple"]["items"] = [{"images": [
            {"slug": "keycap-number-sign", "image": {"source": source}, "status": "CHANGED"}
        ]}]
        sources.images[f"https://em-content.zobj.net/{source}"] = png("red")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            shared = output / "images/apple/keycap.png"
            shared.parent.mkdir(parents=True)
            shared.write_bytes(png("green"))
            (output / "dataset.json").write_text(json.dumps([
                {"unicode": [f"U+{code}", "U+FE0F", "U+20E3"], "name": "keycap", "apple_emoji": {"image_path": str(shared)}}
                for code in ["0023", "002A"]
            ]))
            self.assertEqual(run(output, sources, "apple"), 0)
            entries = json.loads((output / "dataset.json").read_text())
            paths = [Path(entry["apple_emoji"]["image_path"]) for entry in entries]
            self.assertEqual(paths[0], shared)
            self.assertNotEqual(paths[0], paths[1])
            self.assertEqual(paths[0].read_bytes(), png("red"))
            self.assertEqual(paths[1].read_bytes(), png("green"))

    def test_cache_inside_output_is_rejected_before_network_or_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            with patch.object(requests.Session, "get") as get, contextlib.redirect_stderr(io.StringIO()):
                status = emoji_dataset.main(["--output", str(output), "--cache-dir", str(output / "cache")])
            self.assertEqual(status, 1)
            get.assert_not_called()
            self.assertFalse(output.exists())

    def test_rate_limited_catalog_stops_other_requests_to_same_host(self):
        sources = Sources()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            with patch.object(requests.Session, "get", side_effect=sources.get), \
                 patch.object(requests.Session, "post", return_value=response(b"limited", 429, {"Retry-After": "60"})) as post, \
                 contextlib.redirect_stderr(io.StringIO()) as stderr:
                status = emoji_dataset.main(["--output", str(output), "--request-delay", "0"])
            self.assertEqual(status, 1)
            self.assertEqual(post.call_count, 1)
            self.assertIn("Retry-After: 60", stderr.getvalue())
            self.assertFalse(output.exists())

    def test_failed_publication_restores_original(self):
        sources = Sources()
        sources.vendor("apple", "red")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            output.mkdir()
            (output / "dataset.json").write_text("[]\n")
            replace = os.replace

            def fail_staging(source, destination):
                if Path(source).name == "next":
                    raise OSError("simulated publication failure")
                return replace(source, destination)

            with patch.object(os, "replace", side_effect=fail_staging):
                self.assertEqual(run(output, sources, "apple"), 1)
            self.assertEqual((output / "dataset.json").read_text(), "[]\n")
            self.assertEqual(list(output.iterdir()), [output / "dataset.json"])

    def test_failed_publication_and_rollback_keep_recoverable_original(self):
        sources = Sources()
        sources.vendor("apple", "red")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            output.mkdir()
            (output / "dataset.json").write_text("[]\n")
            replace = os.replace

            def fail_after_backup(source, destination):
                if Path(destination) == output:
                    raise OSError("simulated filesystem failure")
                return replace(source, destination)

            with patch.object(os, "replace", side_effect=fail_after_backup):
                self.assertEqual(run(output, sources, "apple"), 1)
            copies = list(Path(directory).rglob("dataset.json"))
            self.assertEqual(len(copies), 1)
            self.assertEqual(copies[0].read_text(), "[]\n")

    def test_vendor_mismatch_rejects_catalog_without_changes(self):
        sources = Sources()
        sources.vendor("apple", "red")
        sources.catalogs["apple"]["items"][0]["images"][0]["image"]["source"] = "source/google/123/grinning-face_1f600.png"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            self.assertEqual(run(output, sources, "apple"), 1)
            self.assertFalse(output.exists())

    def test_all_seven_local_vendor_identifiers_select_expected_sources(self):
        sources = Sources()
        mapping = {"apple": "apple", "emojione": "joypixels", "facebook": "facebook",
                   "google": "noto-color-emoji", "samsung": "samsung", "twitter": "twitter", "windows": "microsoft"}
        for slug in mapping.values():
            sources.vendor(slug, "red")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            self.assertEqual(run(output, sources), 0)
            entry = json.loads((output / "dataset.json").read_text())[0]
            for vendor, slug in mapping.items():
                self.assertIn(f"/source/{slug}/", entry[f"{vendor}_emoji"]["source"]["url"])

    def test_late_invalid_download_rolls_back_vendor_and_keeps_other_vendor_progress(self):
        sources = Sources()
        sources.vendor("apple", "red")
        google = sources.vendor("noto-color-emoji", "blue")
        source = "source/apple/123/waving-hand_light-skin-tone_1f44b-1f3fb_1f3fb.png"
        sources.catalogs["apple"]["items"][0]["images"].append(
            {"slug": "waving-hand-light-skin-tone", "image": {"source": source}, "status": "NEW"}
        )
        sources.images[f"https://em-content.zobj.net/{source}"] = b"GIF89a-not-a-png"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            old_path = output / "images/apple/old name.png"
            old_path.parent.mkdir(parents=True)
            old = png("green")
            old_path.write_bytes(old)
            (output / "dataset.json").write_text(json.dumps([
                {"unicode": ["U+1F600"], "name": "old name", "apple_emoji": {
                    "image_path": str(old_path), "source": {"release": "old"}}}
            ]))
            self.assertEqual(run(output, sources, "apple", "google"), 1)
            self.assertEqual(old_path.read_bytes(), old)
            entries = json.loads((output / "dataset.json").read_text())
            self.assertEqual(entries[0]["apple_emoji"]["source"]["release"], "old")
            self.assertEqual(Path(entries[0]["google_emoji"]["image_path"]).read_bytes(), google)
            self.assertEqual(list((output / "images/apple").iterdir()), [old_path])

    def test_tone_filename_maps_full_sequence_and_preserves_existing_path(self):
        sources = Sources()
        sources.vendor("apple", "red")
        source = "source/apple/123/waving-hand_light-skin-tone_1f44b-1f3fb_1f3fb.png"
        sources.catalogs["apple"]["items"][0]["images"].append(
            {"slug": "waving-hand-light-skin-tone", "image": {"source": source}, "status": "NEW"}
        )
        expected = png("blue")
        sources.images[f"https://em-content.zobj.net/{source}"] = expected
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            old = output / "images/apple/old toned name.png"
            old.parent.mkdir(parents=True)
            old.write_bytes(png("green"))
            (output / "dataset.json").write_text(json.dumps([
                {"unicode": ["U+1F44B", "U+1F3FB"], "name": "old toned name", "apple_emoji": {"image_path": str(old)}}
            ]))
            self.assertEqual(run(output, sources, "apple"), 0)
            entries = json.loads((output / "dataset.json").read_text())
            self.assertEqual(entries[1]["apple_emoji"]["image_path"], str(old))
            self.assertEqual(old.read_bytes(), expected)

    def test_rate_limit_preserves_output_and_cached_download_resumes_later(self):
        sources = Sources()
        sources.vendor("apple", "red")
        source = "source/apple/123/waving-hand_light-skin-tone_1f44b-1f3fb_1f3fb.png"
        sources.catalogs["apple"]["items"][0]["images"].append(
            {"slug": "waving-hand-light-skin-tone", "image": {"source": source}, "status": "NEW"}
        )
        url = f"https://em-content.zobj.net/{source}"
        sources.images[url] = response(b"limited", 429, {"Retry-After": "3600"})
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            output.mkdir()
            index = output / "dataset.json"
            index.write_text("[]\n")
            self.assertEqual(run(output, sources, "apple"), 1)
            self.assertEqual(index.read_text(), "[]\n")
            # A second run can use the first completed download without requesting it again.
            del sources.images["https://em-content.zobj.net/source/apple/123/grinning-face_1f600.png"]
            sources.images[url] = png("blue")
            self.assertEqual(run(output, sources, "apple"), 0)
            self.assertEqual(len(json.loads(index.read_text())), 2)

    def test_names_that_sanitize_identically_have_distinct_images(self):
        sources = Sources()
        sources.vendor("apple", "red")
        sources.unicode = "# Version: 17.0\n0023 FE0F 20E3 ; fully-qualified # #️⃣ E0.6 keycap: #\n002A FE0F 20E3 ; fully-qualified # *️⃣ E2.0 keycap: *\n"
        images = []
        expected = []
        for code, color in [("23", "red"), ("2a", "blue")]:
            source = f"source/apple/123/keycap_{code}-fe0f-20e3.png"
            images.append({"slug": "keycap", "image": {"source": source}, "status": "NEW"})
            data = png(color)
            sources.images[f"https://em-content.zobj.net/{source}"] = data
            expected.append(data)
        sources.catalogs["apple"]["items"] = [{"images": images}]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            self.assertEqual(run(output, sources, "apple"), 0)
            entries = json.loads((output / "dataset.json").read_text())
            paths = [Path(e["apple_emoji"]["image_path"]) for e in entries]
            self.assertNotEqual(paths[0], paths[1])
            self.assertEqual([path.read_bytes() for path in paths], expected)

    def test_missing_new_artwork_preserves_legacy_file_and_marks_unknown_provenance(self):
        sources = Sources()
        sources.vendor("apple", "red")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            legacy = output / "images/apple/waving hand light skin tone.png"
            legacy.parent.mkdir(parents=True)
            old_image = png("green")
            legacy.write_bytes(old_image)
            (output / "dataset.json").write_text("[]")
            self.assertEqual(run(output, sources, "apple"), 0)
            entries = json.loads((output / "dataset.json").read_text())
            retained = entries[1]["apple_emoji"]
            self.assertEqual(Path(retained["image_path"]).read_bytes(), old_image)
            self.assertIsNone(retained["source"]["release"])
            self.assertIsNone(retained["source"]["url"])
            self.assertFalse(retained["source"]["verified"])

    def test_unicode_index_uses_selected_vendor_artwork_and_release(self):
        sources = Sources()
        apple = sources.vendor("apple", "red")
        google = sources.vendor("noto-color-emoji", "blue")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            self.assertEqual(run(output, sources, "apple", "google"), 0)
            entries = json.loads((output / "dataset.json").read_text())
            self.assertEqual([item["unicode"] for item in entries], [["U+1F600"], ["U+1F44B", "U+1F3FB"]])
            for vendor, expected in [("apple", apple), ("google", google)]:
                image = entries[0][f"{vendor}_emoji"]
                self.assertEqual(Path(image["image_path"]).read_bytes(), expected)
                self.assertEqual(image["source"]["release"], "v1")
                self.assertIn(f"/source/{'apple' if vendor == 'apple' else 'noto-color-emoji'}/", image["source"]["url"])

    def test_unexpected_unicode_response_does_not_replace_existing_index(self):
        response = requests.Response()
        response.status_code = 200
        response._content = b"<html>Temporarily unavailable</html>"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            output.mkdir()
            index = output / "dataset.json"
            index.write_text("[]\n")
            with patch.object(requests.Session, "get", return_value=response):
                with contextlib.redirect_stderr(io.StringIO()):
                    status = emoji_dataset.main(["--output", str(output), "--vendor", "apple"])
            self.assertEqual(status, 1)
            self.assertEqual(index.read_text(), "[]\n")

    def test_unavailable_unicode_index_leaves_dataset_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dataset"
            output.mkdir()
            index = output / "dataset.json"
            index.write_text("[]\n")
            with patch.object(requests.Session, "get", side_effect=requests.ConnectionError("offline")):
                with contextlib.redirect_stderr(io.StringIO()):
                    status = emoji_dataset.main(["--output", str(output), "--vendor", "apple"])
            self.assertEqual(status, 1)
            self.assertEqual(index.read_text(), "[]\n")
            self.assertEqual(list(output.iterdir()), [index])


if __name__ == "__main__":
    unittest.main()
