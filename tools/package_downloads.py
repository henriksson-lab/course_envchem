"""Package only the explicit student activity inputs, reproducibly."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ACTIVITIES = {
    "water-analysis": ("aquatic-equilibria", ["water-ions.csv", "corrections.csv",
                                            "water-analysis.R", "water-report.Rmd"]),
    "carbonate-speciation": ("carbonate-gases", ["speciation.R", "report.Rmd"]),
    "contaminant-fate": ("organic-contaminants", ["compounds.csv", "fate.R",
                                                "fate-report.Rmd"]),
}


def package():
    target = ROOT / "downloads"
    target.mkdir(exist_ok=True)
    for name, (folder, files) in ACTIVITIES.items():
        with zipfile.ZipFile(target / f"{name}.zip", "w",
                             compression=zipfile.ZIP_DEFLATED) as archive:
            for filename in files:
                info = zipfile.ZipInfo(filename, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, (ROOT / folder / filename).read_bytes())
    print(f"Packaged {len(ACTIVITIES)} student activities.")


if __name__ == "__main__":
    package()
