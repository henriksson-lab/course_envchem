"""Check rendered local targets, fragment IDs, downloads, and exclusions."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import zipfile
from package_downloads import ACTIVITIES

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if fields.get("id"):
            self.ids.add(fields["id"])
        if tag == "a" and fields.get("name"):
            self.ids.add(fields["name"])
        for name in ("href", "src"):
            if fields.get(name):
                self.links.append(fields[name])


def check():
    pages = {p.resolve(): Page(p.read_text()) for p in DOCS.rglob("*.html")}
    errors = []
    for path, page in pages.items():
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or url.path.startswith("/"):
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target /= "index.html"
            if not target.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing {link}")
            elif url.fragment and target in pages and not url.fragment.startswith("/"):
                if unquote(url.fragment) not in pages[target].ids:
                    errors.append(f"{path.relative_to(ROOT)}: missing fragment {link}")
    for name, (folder, files) in ACTIVITIES.items():
        archive_path = ROOT / "downloads" / f"{name}.zip"
        with zipfile.ZipFile(archive_path) as archive:
            if set(archive.namelist()) != set(files):
                errors.append(f"{name}: unexpected archive contents")
            for filename in files:
                expected = (ROOT / folder / filename).read_bytes()
                if archive.read(filename) != expected:
                    errors.append(f"{name}: stale archive file {filename}")
                published = DOCS / folder / filename
                if not published.exists() or published.read_bytes() != expected:
                    errors.append(f"{name}: missing/stale published input {filename}")
        deployed = DOCS / "downloads" / archive_path.name
        if not deployed.exists() or deployed.read_bytes() != archive_path.read_bytes():
            errors.append(f"{name}: missing/stale published ZIP")
    for excluded in ("instructor", "tools", "templates", "contentplan.html", "README.html"):
        if (DOCS / excluded).exists():
            errors.append(f"Internal content copied to docs: {excluded}")
    if not (DOCS / ".nojekyll").exists():
        errors.append("Missing GitHub Pages .nojekyll marker")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Checked {len(pages)} HTML files, fragment targets, 3 portable archives, "
          "published input copies, and internal-file exclusions.")


if __name__ == "__main__":
    check()
