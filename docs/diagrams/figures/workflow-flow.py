"""From a caller's push to a GitHub Release: the two reusable workflows and what passes between them.

Reads: Two lanes, each read left to right. The top lane runs on every push and pull request: the caller's
esp32-examples-build-ci.yml calls ru-build, whose generate-matrix job checks out espidf-tools and turns
app_config.yml into a matrix, whose build job runs once per matrix entry in the espressif/idf image, and whose
size-report job comments a size table on pull requests. The build job uploads one fw-* artifact per entry. The
bottom lane runs when a version tag is pushed: the caller's release.yml calls ru-release-with-artifacts, which
downloads those artifacts for the tagged commit and attaches them to a GitHub Release, so nothing is rebuilt. Solid
arrows mean "runs next", dashed arrows carry files. Job names are read from the workflow files.
"""

import yaml

from kokeb_mkdocs_theme.figkit import Fig
from kokeb_mkdocs_theme.paths import repo_root

ROOT = repo_root()
BUILD = ".github/workflows/ru-build.yml"
RELEASE = ".github/workflows/ru-release-with-artifacts.yml"


def _jobs(path):
    doc = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    return [(jid, " ".join(str(j.get("name", jid)).split())) for jid, j in doc["jobs"].items()]


def data():
    return {
        "build_jobs": [j for j, _ in _jobs(BUILD)],
        "release_jobs": [j for j, _ in _jobs(RELEASE)],
        "sources": [f"{BUILD}:jobs", f"{RELEASE}:jobs"],
    }


TEXT = {
    "generate-matrix": ("", ["checks out espidf-tools", "app_config.yml becomes a matrix"]),
    "build": ("× N", ["one job per matrix entry", "in the espressif/idf image"]),
    "size-report": ("PR only", ["comments a size table", "optional size budget"]),
}


def build(d):
    f = Fig(
        "workflow-flow",
        "From push to release",
        alt="Two-lane flow: on every push and pull request ru-build runs generate-matrix, build and size-report and "
        "uploads fw-* artifacts; on a version tag ru-release-with-artifacts downloads those same artifacts and "
        "attaches them to a GitHub Release.",
        width=1200,
        kicker="Workflows",
        subtitle="Firmware is built once, on every push. A version tag only ships what was already built.",
        profile="overview",
        legend=[("brand", "job in ci-tools"), ("slate", "kept by GitHub"), ("~solid", "runs next"),
                ("~dashed", "passes files")],
    )
    W = f.body_w
    gap, H = 56, 118
    cw = (W - 32 - 2 * gap) / 3
    col = [16 + i * (cw + gap) for i in range(3)]

    # Lane 1: every push and pull request.
    inner = f.region_inner_top(0, sub_below=True)
    lane1 = f.region(0, 0, W, inner + H + 20, "Every push and pull request", tone="slate",
                     sub="your esp32-examples-build-ci.yml calls ru-build.yml", sub_below=True)
    jobs = []
    for i, job in enumerate(d["build_jobs"][:3]):
        tag, lines = TEXT.get(job, ("", []))
        jobs.append(f.card(col[i], inner, cw, job, lines, tone="brand", accent=True, h=H, tag=tag))
    for a, b in zip(jobs, jobs[1:]):
        f.connect(a, b, "right", "left")

    art = f.card(col[1], lane1.b + 64, cw, "fw-* artifacts", ["fw-<app>-<idf>-<type>"], sub="one per entry, kept 7 days",
                 tone="slate", accent=True, mono=True)
    f.connect(jobs[1], art, "bottom", "top", dashed=True, label="uploads")

    # Lane 2: a version tag.
    top2 = art.b + 64
    inner2 = f.region_inner_top(top2, sub_below=True)
    f.region(0, top2, W, inner2 - top2 + H + 20, "A version tag v*.*.*", tone="slate",
             sub="your release.yml calls ru-release-with-artifacts.yml", sub_below=True)
    f.note(col[0], inner2, cw, "No rebuild: the release ships the firmware CI already built and tested.")
    rel = f.card(col[1], inner2, cw, d["release_jobs"][0], ["finds the fw-* artifacts", "of the tagged commit"],
                 tone="brand", accent=True, h=H)
    gh = f.card(col[2], inner2, cw, "GitHub Release", ["generated notes", "every firmware attached"],
                tone="slate", accent=True, h=H)
    f.connect(art, rel, "bottom", "top", dashed=True, label="downloads", label_at=0.35)
    f.connect(rel, gh, "right", "left")
    return f
