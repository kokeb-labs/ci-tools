"""Figure kinds drawn from a small model file (``docs/model/<id>.<kind>.yml``).

``from_model(path)`` reads a model, checks it against its kind's schema, and returns the finished ``Fig``. A figure
module is then three lines::

    from kokeb_mkdocs_theme.figkit.kinds import from_model

    SOURCES = ["docs/model/handler-health.state.yml"]


    def build(_data):
        return from_model("docs/model/handler-health.state.yml")

The kinds: ``state``, ``graph``, ``seq``, ``timeline``, ``matrix``, ``bytes`` and ``pipeline``; ``kinds.KINDS`` maps a
name to its module (each has ``validate(model, where)`` and ``build(model, lock_dir, where)``).
"""

from __future__ import annotations

import importlib
import pathlib

import yaml

from ._common import ModelError

#: kind name -> module name in this package
KINDS = {
    "state": "state",
    "graph": "graph",
    "seq": "seq",
    "timeline": "timeline",
    "matrix": "matrix",
    "bytes": "bytelayout",
    "pipeline": "pipeline",
}

#: Kinds that need a layout lock (Graphviz is run once by ``kokeb-docs figkit layout``).
LAYOUT_KINDS = ("state", "graph")


def module(kind: str):
    if kind not in KINDS:
        raise SystemExit(f"[figkit] unknown figure kind {kind!r}; kinds: {', '.join(KINDS)}")
    return importlib.import_module(f".{KINDS[kind]}", __name__)


def load_model(source) -> tuple[dict, str]:
    """(model, where) from a path or a dict."""
    if isinstance(source, dict):
        return source, "model"
    path = pathlib.Path(source)
    if not path.is_absolute():
        from ...paths import repo_root

        path = repo_root() / path
    try:
        model = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        raise SystemExit(f"[figkit] {source}: {e}") from e
    if not isinstance(model, dict):
        raise SystemExit(f"[figkit] {source}: a model is a mapping")
    return model, str(source)


def from_model(source, lock_dir=None):
    """Build the figure of a model file (or dict). ``lock_dir`` holds ``<id>.layout.json`` (default: the repository's
    ``docs/diagrams``)."""
    model, where = load_model(source)
    if lock_dir is None:
        from ...paths import repo_root

        lock_dir = repo_root() / "docs/diagrams"
    kind = model.get("kind")
    fig = module(str(kind)).build(model, pathlib.Path(lock_dir), where)
    if isinstance(source, (str, pathlib.Path)):
        fig.model_sources = [str(source)]
    return fig


__all__ = ["KINDS", "LAYOUT_KINDS", "ModelError", "from_model", "load_model", "module"]
