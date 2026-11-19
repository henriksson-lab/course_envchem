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
    demo_sources = [*sorted((ROOT / "demos").glob("*.js")), ROOT / "demos" / "demo.css"]
    for source in demo_sources:
        published = DOCS / "demos" / source.name
        if not published.exists() or published.read_bytes() != source.read_bytes():
            errors.append(f"Missing/stale published demo asset: {source.name}")
    for week in range(1, 6):
        page = DOCS / "interactives" / f"week{week}.html"
        if not page.exists() or 'data-demo=' not in page.read_text():
            errors.append(f"Missing weekly interactive mount: {page.name}")
    exercise_models = {
        "deposition": "deposition", "carbonate-gases": "carbonate",
        "metals": "metals", "organic-contaminants": "fate", "integrated-case": "catchment",
    }
    for folder, model in exercise_models.items():
        exercise = DOCS / folder / "exercise.html"
        lecture = DOCS / folder / "lec.html"
        for page in (exercise, lecture):
            text = page.read_text() if page.exists() else ""
            if f'data-demo="{model}"' not in text or 'id="explore"' not in text:
                errors.append(f"Missing embedded {model} demo at {page.relative_to(DOCS)}#explore")
        target = f"{folder}/exercise.html#explore"
        # The restored scaffold must expose the actual exercise demo in the menu.
        if target not in (DOCS / "index.html").read_text():
            errors.append(f"Missing sidebar demo link: {target}")
    for excluded in ("instructor", "tools", "templates", "contentplan.html", "README.html",
                     "demos/tests", "demos/README.md"):
        if (DOCS / excluded).exists():
            errors.append(f"Internal content copied to docs: {excluded}")
    if not (DOCS / ".nojekyll").exists():
        errors.append("Missing GitHub Pages .nojekyll marker")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Checked {len(pages)} HTML files, fragment targets, 3 portable archives, "
          "published input copies, 5 weekly demos/assets, and internal-file exclusions.")


if __name__ == "__main__":
    check()
