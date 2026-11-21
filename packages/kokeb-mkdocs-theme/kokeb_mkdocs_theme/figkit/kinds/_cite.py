"""Datasheet citations for the bus figures (``timing``, ``topology``): every number a figure prints names the
section and page it comes from, and a number without one fails the build.

A model names its citations under ``refs`` (``{name: {doc, section, page}}``, the same form as ``docs/hardware.yml``);
a name it does not define is looked up in the repository's ``docs/hardware.yml``, so a driver cites the sections it
already lists once. ``doc`` must be a document of ``docs/datasheets.yml`` (or of ``hardware.yml``'s ``documents``)
when the repository has either file.
"""

from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass

import yaml

#: A number in free text: a digit run (a "0x1F" or "2.5" counts once). Letters glued to a digit before it (a pin
#: name such as "SDO1", a part "TMC5160") are not a number.
NUMBER = re.compile(r"\b\d")


@dataclass(frozen=True)
class Ref:
    name: str
    doc: str
    section: str
    page: int

    def short(self) -> str:
        sec = self.section.split(" ")[0] if self.section[:1].isdigit() else self.section
        return f"{sec}, p. {self.page}"

    def long(self) -> str:
        return f"{self.section}, p. {self.page}"


def has_number(text: str) -> bool:
    return bool(NUMBER.search(str(text or "")))


def _repo_root():
    try:
        from ...paths import repo_root

        return repo_root()
    except (Exception, SystemExit):  # noqa: BLE001 - no repository (a dict model in a test): nothing to fall back to
        return None


def _yaml(path: pathlib.Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}


class Citations:
    """The citations a model may use. ``use(name, path)`` resolves one and records a problem when it cannot."""

    def __init__(self, check, model: dict, root=None):
        self.c = check
        self.refs: dict[str, Ref] = {}
        self.used: list[Ref] = []
        root = _repo_root() if root is None else root
        docs: set[str] | None = None
        hw_refs: dict = {}
        if root is not None:
            root = pathlib.Path(root)
            ds = _yaml(root / "docs/datasheets.yml") if (root / "docs/datasheets.yml").is_file() else {}
            hw = _yaml(root / "docs/hardware.yml") if (root / "docs/hardware.yml").is_file() else {}
            ids = {str(d.get("id")) for d in (ds.get("documents") or []) if isinstance(d, dict)}
            ids |= {str(d.get("id")) for d in (hw.get("documents") or []) if isinstance(d, dict)}
            docs = ids or None
            hw_refs = hw.get("refs") or {} if isinstance(hw, dict) else {}
        raw = model.get("refs") or {}
        if not isinstance(raw, dict):
            check.bad("refs: a mapping of name to {doc, section, page}")
            raw = {}
        for src, table in (("refs", raw), ("hardware.yml refs", hw_refs)):
            for name, r in (table or {}).items():
                if name in self.refs:
                    continue
                p = f"{src}.{name}"
                if not isinstance(r, dict) or not {"doc", "section", "page"} <= set(r):
                    if src == "refs":
                        check.bad(f"{p}: needs doc, section and page")
                    continue
                if src == "refs":
                    for k in sorted(set(r) - {"doc", "section", "page"}):
                        check.bad(f"{p}: unknown key {k!r} (allowed: doc, page, section)")
                page = r.get("page")
                if not isinstance(page, int) or isinstance(page, bool) or page < 1:
                    if src == "refs":
                        check.bad(f"{p}.page: the printed page number, not {page!r}")
                    continue
                if docs is not None and str(r["doc"]) not in docs:
                    if src == "refs":
                        check.bad(f"{p}.doc: {r['doc']!r} is not a document of docs/datasheets.yml "
                                  f"({', '.join(sorted(docs))})")
                    continue
                if not str(r.get("section") or "").strip():
                    if src == "refs":
                        check.bad(f"{p}.section: the datasheet's own section heading")
                    continue
                self.refs[str(name)] = Ref(str(name), str(r["doc"]), str(r["section"]), page)

    def use(self, name, path: str, why: str = "") -> Ref | None:
        """The citation ``name`` (from ``path``); a problem when it is missing or unknown."""
        if name in (None, ""):
            self.c.bad(f"{path}: no datasheet reference (ref:){' for ' + why if why else ''}; every number needs one")
            return None
        r = self.refs.get(str(name))
        if r is None:
            self.c.bad(f"{path}: unknown ref {name!r}; define it under refs (or in docs/hardware.yml refs)"
                       + (f"; known: {', '.join(sorted(self.refs))}" if self.refs else ""))
            return None
        if r not in self.used:
            self.used.append(r)
        return r

    def text_needs_ref(self, obj: dict, path: str, keys=("text", "label", "note", "detail")) -> Ref | None:
        """An item whose text holds a number must cite where the number comes from (``ref``)."""
        if any(has_number(obj.get(k, "")) for k in keys):
            return self.use(obj.get("ref"), f"{path}.ref", "the number in its text")
        if obj.get("ref") not in (None, ""):
            return self.use(obj.get("ref"), f"{path}.ref")
        return None

    def todo(self) -> list[str]:
        """Problems for the build (not the schema, so a scaffold validates): a cited section still marked TODO."""
        return [f"ref {r.name!r}: TODO: write the datasheet's own section heading and page" for r in self.used
                if "TODO" in r.section]

    def sources_line(self) -> str:
        """``Datasheet: 7.6 Timing requirements, p. 9; ...`` for the citations the figure used, in first-use order."""
        if not self.used:
            return ""
        docs = sorted({r.doc for r in self.used})
        lead = "Datasheet" if len(docs) == 1 else "Sources"
        return f"{lead}: " + "; ".join((f"{r.doc} " if len(docs) > 1 else "") + r.long() for r in self.used) + "."


__all__ = ["Citations", "NUMBER", "Ref", "has_number"]
