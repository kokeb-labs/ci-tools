#!/usr/bin/env python3
"""Layering checker: includes, platform code, keywords, CMake target links and linked symbols, by a rules file.
Standard library plus PyYAML.

  layering.py check  --root DIR --rules FILE [--boundary-files FILE] [--compile-db FILE] [--graphviz FILE]
                     [--objects DIR] [--denylist FILE] [--exclude "glob ..."] [--report-dir DIR] [--summary FILE]
                     [--github-output FILE] [--annotate-prefix PATH] [--enforce true|false]
  layering.py fixtures --dir DIR --rules FILE [--boundary-files FILE]
  layering.py poison --rules FILE --out DIR [--extra DIR]

The rules file (paths are globs from --root; ** spans folders):

  zones:                 name -> {paths: [globs], may_include: [names], boundary_files: FILE, violation_id: LAY-NNN}
                         A file belongs to the first zone whose paths match it. may_include names zones, groups of
                         public_headers, header_groups, std_subset, std_any, sdk (an SDK or RTOS header, in a file
                         listed in a boundary file) and sdk_any (an SDK header in any file of the zone).
  public_headers:        name -> glob (a group of headers, e.g. a part's public headers)
  header_groups:         name -> [globs] of headers that are not in the tree (e.g. gtest: ["gtest/*", "gmock/*"])
  boundary_files:        FILE with boundary_files: [{path, sdk, status: present|planned}]
  sdk_headers:           [globs] of SDK and RTOS headers
  std_subset:            [headers] of the standard library a zone with std_subset may use (default: a freestanding
                         subset); std_any allows every standard header
  forbidden_keywords:    [words] never in code (comments and strings excluded)
  platform_macros:       [globs] of macros tested by #if/#ifdef/defined() only in boundary files and sdk zones
  external_zones:        [zone names] whose files are include targets but are not checked (another CI checks them)
  denylist_file:         FILE of names that must not appear anywhere (one per line); --denylist overrides
  unresolved:            error (default) or ignore: an include that is neither in the tree, standard, SDK nor in a
                         header group
  forbidden_patterns:    [{id, regex, paths: [globs], exclude: [globs], message}] on the text of matching files
  targets:               {layers: [[target globs], ...] lowest first, private_only: [target globs],
                          forbidden: [{from: glob, to: glob}]} on the cmake --graphviz output (--graphviz)
  symbols:               {forbidden: [regex], exempt_sources: [globs]} on `nm` of every object under --objects

Rule ids: LAY-001 an include a zone may not use (or zone violation_id), LAY-002 an SDK include outside a boundary
file or in a boundary header, LAY-003 a boundary file included by another file, LAY-006 a CMake link against the
layers, LAY-007 a platform macro outside boundary files and sdk zones, LAY-008 the boundary list does not match the
tree, LAY-009 a denylisted name, LAY-012 a forbidden keyword, SYM-001 a linked object references a forbidden
symbol, and the ids of forbidden_patterns. Output: one line per finding, SARIF 2.1.0 and JSON in --report-dir, a step
summary, exit 1 on a finding (with --enforce true). There is no suppression: a rule change is a change to the rules.

fixtures: DIR/good/ must give no finding; each DIR/bad/<case>/ must give exactly the rule ids of its expect.txt.
A fixture uses its own rules.yml (and boundary-files.yml) when it has one, else --rules.

poison: writes a header that stops the build (#error) for every SDK header name of sdk_headers, plus common names
under each glob's folder, and copies --extra over them; the poison build puts DIR first on the system include path.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from functools import lru_cache

import yaml

SOURCE_EXT = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".ipp", ".inl", ".tpp")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}
SKIP_PREFIX = ("build", ".ru-", "_build", "cmake-build")

STD_CXX = set("""algorithm any array atomic barrier bit bitset charconv chrono codecvt compare complex concepts
condition_variable coroutine deque exception execution expected filesystem flat_map flat_set format forward_list
fstream functional future generator initializer_list iomanip ios iosfwd iostream istream iterator latch limits list
locale map mdspan memory memory_resource mutex new numbers numeric optional ostream print queue random ranges ratio
regex scoped_allocator semaphore set shared_mutex source_location span spanstream sstream stack stacktrace stdexcept
stdfloat stop_token streambuf string string_view strstream syncstream system_error thread tuple type_traits
typeindex typeinfo unordered_map unordered_set utility valarray variant vector version cassert cctype cerrno cfenv
cfloat cinttypes climits clocale cmath csetjmp csignal cstdarg cstddef cstdint cstdio cstdlib cstring ctime cuchar
cwchar cwctype ciso646 cstdalign cstdbool ccomplex ctgmath""".split())
STD_C = set("""assert.h complex.h ctype.h errno.h fenv.h float.h inttypes.h iso646.h limits.h locale.h math.h setjmp.h
signal.h stdalign.h stdarg.h stdatomic.h stdbit.h stdbool.h stdckdint.h stddef.h stdint.h stdio.h stdlib.h
stdnoreturn.h string.h tgmath.h threads.h time.h uchar.h wchar.h wctype.h""".split())
# Freestanding-friendly headers (no heap, no exceptions, no I/O), the default std_subset.
STD_SUBSET = set("""algorithm array atomic bit cassert cerrno cfloat charconv cinttypes climits cmath compare concepts
cstddef cstdint cstring expected functional initializer_list iterator limits new numbers numeric optional ratio
source_location span string_view tuple type_traits utility variant version""".split())
COMMON_SDK = {
    "freertos/": ["FreeRTOS.h", "task.h", "queue.h", "semphr.h", "event_groups.h", "timers.h", "stream_buffer.h"],
    "driver/": ["gpio.h", "spi_master.h", "i2c_master.h", "uart.h", "rmt_tx.h", "ledc.h", "adc.h", "twai.h"],
    "hal/": ["gpio_types.h", "spi_types.h"],
    "soc/": ["soc.h", "gpio_num.h"],
    "esp_": ["esp_err.h", "esp_log.h", "esp_timer.h", "esp_system.h", "esp_attr.h", "esp_intr_alloc.h"],
    "stm32": ["stm32f4xx_hal.h", "stm32f4xx.h", "stm32g4xx_hal.h", "stm32h7xx_hal.h"],
    "cmsis_os": ["cmsis_os.h", "cmsis_os2.h"],
}
INCLUDE_RX = re.compile(r'^[ \t]*#[ \t]*include[ \t]*([<"])([^>"\n]+)[>"]', re.M)
COND_RX = re.compile(r"^[ \t]*#[ \t]*(?:if|ifdef|ifndef|elif|elifdef|elifndef)\b(.*)$", re.M)
POISON_MARK = "ru-layering poison"


@lru_cache(maxsize=4096)
def glob_rx(pattern: str) -> re.Pattern:
    out, i = [], 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def gmatch(path: str, patterns) -> bool:
    return any(glob_rx(p).match(path) for p in patterns or [])


def mask(text: str, strings: bool = True) -> str:
    """Comments (and string or character literals, with strings) replaced by spaces, newlines kept."""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        if text.startswith("//", i):
            e = text.find("\n", i)
            e = n if e < 0 else e
            out[i:e] = " " * (e - i)
            i = e
        elif text.startswith("/*", i):
            e = text.find("*/", i + 2)
            e = n if e < 0 else e + 2
            for x in range(i, e):
                if out[x] != "\n":
                    out[x] = " "
            i = e
        elif text[i] in "\"'" and not (text[i] == "'" and i > 0 and text[i - 1].isalnum()):
            q, j = text[i], i + 1
            while j < n and text[j] != q and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            e = min(j + 1, n)
            if strings:
                out[i:e] = " " * (e - i)
            i = e
        else:
            i += 1
    return "".join(out)


class Rules:
    def __init__(self, path: str, root: str, boundary_override: str = "", denylist_override: str = ""):
        with open(path, encoding="utf-8") as fh:
            r = yaml.safe_load(fh) or {}
        self.path = path
        self.zones: dict[str, dict] = r.get("zones") or {}
        self.public = {k: v for k, v in (r.get("public_headers") or {}).items()}
        self.groups = {k: list(v or []) for k, v in (r.get("header_groups") or {}).items()}
        self.sdk = list(r.get("sdk_headers") or [])
        self.std_subset = set(r.get("std_subset") or STD_SUBSET)
        self.keywords = list(r.get("forbidden_keywords") or [])
        self.macros = list(r.get("platform_macros") or [])
        self.external = set(r.get("external_zones") or [])
        self.unresolved = str(r.get("unresolved") or "error")
        self.patterns = list(r.get("forbidden_patterns") or [])
        self.targets = r.get("targets") or {}
        self.symbols = r.get("symbols") or {}
        files = [boundary_override] if boundary_override else ([r["boundary_files"]] if r.get("boundary_files")
                                                              else [])
        files += [z["boundary_files"] for z in self.zones.values() if isinstance(z, dict) and z.get("boundary_files")]
        self.boundary_lists = []
        self.boundary: dict[str, dict] = {}
        for f in dict.fromkeys(files):
            full = os.path.join(root, f)
            self.boundary_lists.append(f)
            if not os.path.isfile(full):
                continue
            with open(full, encoding="utf-8") as fh:
                doc = yaml.safe_load(fh) or {}
            for e in doc.get("boundary_files") or []:
                self.boundary[str(e.get("path"))] = dict(e, list=f)
        deny = denylist_override or r.get("denylist_file") or ""
        self.denylist: list[str] = []
        if deny:
            full = deny if os.path.isabs(deny) else os.path.join(root, deny)
            if os.path.isfile(full):
                with open(full, encoding="utf-8") as fh:
                    self.denylist = [w.strip() for w in fh if w.strip() and not w.startswith("#")]

    def zone_of(self, rel: str) -> str | None:
        for name, z in self.zones.items():
            if gmatch(rel, (z or {}).get("paths")):
                return name
        return None

    def groups_of(self, rel: str) -> set[str]:
        out = {n for n, g in self.public.items() if gmatch(rel, [g] if isinstance(g, str) else g)}
        z = self.zone_of(rel)
        if z:
            out.add(z)
        return out

    def is_sdk(self, header: str) -> bool:
        return any(fnmatch.fnmatchcase(header, p) or fnmatch.fnmatchcase(os.path.basename(header), p)
                   for p in self.sdk)


def walk(root: str, exclude: list[str]) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
        rel_dir = "" if rel_dir == "." else rel_dir + "/"
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(SKIP_PREFIX)
                             and not gmatch(rel_dir + d, exclude) and not gmatch(rel_dir + d + "/", exclude))
        for f in sorted(filenames):
            rel = rel_dir + f
            if not gmatch(rel, exclude):
                out.append(rel)
    return out


def include_dirs(root: str, compile_db: str, files: list[str]) -> list[str]:
    """Include search folders, relative to root: from the compile database, else every inc/ and include/ folder."""
    dirs: list[str] = []
    if compile_db and os.path.isfile(compile_db):
        with open(compile_db, encoding="utf-8") as fh:
            db = json.load(fh)
        for e in db:
            args = e.get("arguments") or shlex.split(e.get("command", ""))
            cwd = e.get("directory", root)
            i = 0
            while i < len(args):
                a, d = args[i], None
                if a in ("-I", "-isystem", "-iquote", "-idirafter") and i + 1 < len(args):
                    d = args[i + 1]
                    i += 1
                elif a.startswith("-I") and len(a) > 2:
                    d = a[2:]
                elif a.startswith("-isystem") and len(a) > 8:
                    d = a[8:]
                i += 1
                if d is None:
                    continue
                rel = os.path.relpath(os.path.normpath(os.path.join(cwd, d)), root).replace(os.sep, "/")
                if not rel.startswith("..") and rel not in dirs:
                    dirs.append(rel)
    if not dirs:
        for f in files:
            parts = f.split("/")
            for i, p in enumerate(parts[:-1]):
                if p in ("inc", "include"):
                    d = "/".join(parts[: i + 1])
                    if d not in dirs:
                        dirs.append(d)
    return dirs


class Checker:
    def __init__(self, root: str, rules: Rules, exclude: list[str], compile_db: str = ""):
        self.root, self.rules = os.path.abspath(root), rules
        self.files = walk(self.root, exclude)
        self.fileset = set(self.files)
        self.dirs = include_dirs(self.root, compile_db, self.files)
        self.findings: list[dict] = []

    def add(self, rule: str, path: str, line: int, msg: str) -> None:
        self.findings.append({"rule": rule, "path": path, "line": line, "message": msg})

    def resolve(self, src: str, header: str, quoted: bool) -> str | None:
        cands = []
        if quoted:
            cands.append(os.path.normpath(os.path.join(os.path.dirname(src), header)).replace(os.sep, "/"))
        cands += [os.path.normpath(os.path.join(d, header)).replace(os.sep, "/") for d in self.dirs]
        for c in cands:
            if c in self.fileset:
                return c
        return None

    def sdk_zone(self, zone: str | None) -> bool:
        may = set((self.rules.zones.get(zone) or {}).get("may_include") or []) if zone else set()
        return bool(may & {"sdk", "sdk_any"})

    def run(self, denylist_words: list[str] | None = None) -> None:
        r = self.rules
        sources = [f for f in self.files if f.endswith(SOURCE_EXT)]
        for path, e in sorted(r.boundary.items()):
            status = str(e.get("status", "present"))
            if status not in ("present", "planned"):
                self.add("LAY-008", e["list"], 1, f"{path}: status must be present or planned, not {status}")
            elif status == "present" and path not in self.fileset:
                self.add("LAY-008", e["list"], 1, f"{path} is listed as present but does not exist")
            elif status == "planned" and path in self.fileset:
                self.add("LAY-008", e["list"], 1, f"{path} exists but is listed as planned; mark it present")
        for f in sources:
            zone = r.zone_of(f)
            if zone in r.external:
                continue
            with open(os.path.join(self.root, f), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            if zone is not None:
                self.check_includes(f, zone, text)
                self.check_macros(f, zone, text)
                self.check_keywords(f, text)
        for f in self.files:
            zone = r.zone_of(f)
            if zone in r.external:
                continue
            if (r.denylist or denylist_words) and (zone is not None or os.path.basename(f) == "CMakeLists.txt"
                                                   or f.endswith((".cmake", ".md", ".yml", ".yaml"))):
                self.check_denylist(f, denylist_words or r.denylist)
            for p in r.patterns:
                if gmatch(f, p.get("paths") or ["**"]) and not gmatch(f, p.get("exclude")):
                    self.check_pattern(f, p)

    def check_includes(self, f: str, zone: str, text: str) -> None:
        r = self.rules
        z = r.zones[zone] or {}
        may = set(z.get("may_include") or []) | {zone}  # a zone may always include its own files
        vid = z.get("violation_id") or "LAY-001"
        listed = f in r.boundary
        text = mask(text, strings=False)
        for m in INCLUDE_RX.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            quoted, header = m.group(1) == '"', m.group(2).strip()
            target = self.resolve(f, header, quoted)
            if target is not None:
                if target in r.boundary and target != f:
                    self.add("LAY-003", f, line, f"includes the boundary file {target}; boundary files are "
                                                 "compiled, never included")
                    continue
                groups = r.groups_of(target)
                if not groups:
                    if r.unresolved == "error":
                        self.add(vid, f, line, f"includes {target}, which is in no zone of the rules")
                    continue
                if not (groups & may):
                    self.add(vid, f, line, f"zone {zone} may not include {target} (zone "
                                           f"{', '.join(sorted(groups))})")
                continue
            if r.is_sdk(header):
                if "sdk_any" in may:
                    continue
                if "sdk" not in may or not listed:
                    self.add("LAY-002", f, line, f"SDK or RTOS header <{header}> outside a file listed in "
                                                 f"{', '.join(r.boundary_lists) or 'a boundary file list'}")
                elif not f.endswith((".c", ".cc", ".cpp", ".cxx")):
                    self.add("LAY-002", f, line, f"SDK or RTOS header <{header}> in the boundary header {f}; only a "
                                                 "boundary source file may include it")
                continue
            base = header
            if base in STD_CXX or base in STD_C:
                if "std_any" in may:
                    continue
                if "std_subset" in may and base in r.std_subset:
                    continue
                self.add(vid, f, line, f"zone {zone} may not use the standard header <{header}> "
                                       f"({'not in std_subset' if 'std_subset' in may else 'no standard headers'})")
                continue
            hit = [g for g, globs in r.groups.items() if any(fnmatch.fnmatchcase(header, x) for x in globs)]
            if hit:
                if not (set(hit) & may):
                    self.add(vid, f, line, f"zone {zone} may not include <{header}> (group {', '.join(hit)})")
                continue
            if r.unresolved == "error":
                self.add(vid, f, line, f"cannot resolve {header!r}: not in the tree on the include path, not "
                                       "standard, not an SDK header and in no header group")

    def check_macros(self, f: str, zone: str, text: str) -> None:
        r = self.rules
        if not r.macros or f in r.boundary or self.sdk_zone(zone):
            return
        masked = mask(text)
        for m in COND_RX.finditer(masked):
            for ident in re.findall(r"[A-Za-z_]\w*", m.group(1)):
                if ident != "defined" and any(fnmatch.fnmatchcase(ident, p) for p in r.macros):
                    line = masked.count("\n", 0, m.start()) + 1
                    self.add("LAY-007", f, line, f"tests the platform macro {ident} outside a boundary file")

    def check_keywords(self, f: str, text: str) -> None:
        if not self.rules.keywords:
            return
        masked = mask(text)
        for kw in self.rules.keywords:
            for m in re.finditer(rf"\b{re.escape(kw)}\b", masked):
                line = masked.count("\n", 0, m.start()) + 1
                self.add("LAY-012", f, line, f"the keyword `{kw}` is not allowed")

    def check_denylist(self, f: str, words: list[str]) -> None:
        try:
            with open(os.path.join(self.root, f), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            return
        for idx, w in enumerate(words, 1):
            for m in re.finditer(rf"(?i)(?<![A-Za-z0-9]){re.escape(w)}(?![A-Za-z0-9])", text):
                line = text.count("\n", 0, m.start()) + 1
                # The name itself is never printed: the list is private.
                self.add("LAY-009", f, line, f"a denylisted name (entry {idx} of the denylist)")

    def check_pattern(self, f: str, p: dict) -> None:
        try:
            with open(os.path.join(self.root, f), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            return
        for m in re.finditer(p["regex"], text, re.M):
            line = text.count("\n", 0, m.start()) + 1
            self.add(str(p.get("id", "LAY-000")), f, line, str(p.get("message", f"matches {p['regex']}")))

    def check_targets(self, dot: str) -> None:
        t = self.rules.targets
        if not t or not dot or not os.path.isfile(dot):
            return
        with open(dot, encoding="utf-8") as fh:
            text = fh.read()
        text = re.sub(r"subgraph clusterLegend \{.*?\n\}", "", text, flags=re.S)
        labels = dict(re.findall(r'"(node\d+)" \[ label = "([^"]+)"', text))
        edges = []
        for a, b, style in re.findall(r'"(node\d+)" -> "(node\d+)"(?:\s*\[\s*style = (\w+)\s*\])?', text):
            kind = {"dotted": "PRIVATE", "dashed": "INTERFACE"}.get(style, "PUBLIC")
            edges.append((labels.get(a, a), labels.get(b, b), kind))
        layers = [list(x) if isinstance(x, list) else [x] for x in (t.get("layers") or [])]

        def layer(name: str) -> int | None:
            for i, globs in enumerate(layers):
                if any(fnmatch.fnmatchcase(name, g) for g in globs):
                    return i
            return None
        for a, b, kind in edges:
            la, lb = layer(a), layer(b)
            if la is not None and lb is not None and lb > la:
                self.add("LAY-006", os.path.basename(dot), 1, f"{a} links {b} ({kind}), a higher layer")
            if any(fnmatch.fnmatchcase(b, g) for g in t.get("private_only") or []) and kind != "PRIVATE":
                self.add("LAY-006", os.path.basename(dot), 1, f"{a} links {b} {kind}; it may be linked PRIVATE only")
            for rule in t.get("forbidden") or []:
                if fnmatch.fnmatchcase(a, str(rule.get("from"))) and fnmatch.fnmatchcase(b, str(rule.get("to"))):
                    self.add("LAY-006", os.path.basename(dot), 1, f"{a} may not link {b}")

    def check_symbols(self, objects: str, compile_db: str) -> int:
        s = self.rules.symbols
        default = [r"^(esp_|xTask|vTask|xQueue|xSemaphore|xEventGroup|xTimer|xStream|pvPortMalloc|vPortFree|"
                   r"tx_|_tx_|HAL_|osKernel|osThread|osMutex|osSemaphore|osMessageQueue|osEventFlags)"]
        forbidden = [re.compile(x) for x in (s.get("forbidden") or (default if self.rules.sdk else []))]
        if not forbidden or not objects or not os.path.isdir(objects) or not shutil.which("nm"):
            return 0
        exempt_src = set()
        sources_of: dict[str, str] = {}
        if compile_db and os.path.isfile(compile_db):
            with open(compile_db, encoding="utf-8") as fh:
                for e in json.load(fh):
                    src = os.path.relpath(os.path.join(e.get("directory", ""), e["file"]), self.root)
                    src = src.replace(os.sep, "/")
                    out = e.get("output") or ""
                    if out:
                        sources_of[os.path.basename(out)] = src
                    zone = self.rules.zone_of(src)
                    if (src in self.rules.boundary or self.sdk_zone(zone)
                            or gmatch(src, s.get("exempt_sources")) or zone in self.rules.external):
                        exempt_src.add(os.path.basename(out) if out else os.path.basename(src) + ".o")
        files = []
        for dirpath, _, names in os.walk(objects):
            files += [os.path.join(dirpath, n) for n in names if n.endswith((".o", ".obj", ".a"))]
        checked = 0
        for path in sorted(files):
            p = subprocess.run(["nm", "-A", "-u", path], capture_output=True, text=True)
            checked += 1
            for line in p.stdout.splitlines():
                head, _, sym = line.rpartition(" ")
                member = head.split(":")[-2] if head.count(":") >= 2 else os.path.basename(path)
                if os.path.basename(member) in exempt_src:
                    continue
                if any(rx.search(sym) for rx in forbidden):
                    src = sources_of.get(os.path.basename(member), os.path.relpath(path, objects))
                    self.add("SYM-001", src, 1, f"{os.path.basename(member)} references the platform symbol {sym}")
        return checked


def run_check(root, rules_path, boundary, compile_db, exclude, denylist="", graphviz="", objects=""):
    rules = Rules(rules_path, root, boundary, denylist)
    c = Checker(root, rules, exclude, compile_db)
    c.run()
    c.check_targets(graphviz)
    nobj = c.check_symbols(objects, compile_db)
    c.findings.sort(key=lambda f: (f["path"], f["line"], f["rule"], f["message"]))
    return c, nobj


def sarif(findings, prefix: str) -> dict:
    ids = sorted({f["rule"] for f in findings})
    return {"$schema": "https://json.schemastore.org/sarif-2.1.0.json", "version": "2.1.0", "runs": [{
        "tool": {"driver": {"name": "ci-tools layering", "informationUri":
                            "https://github.com/kokeb-labs/ci-tools/blob/main/docs/ru-layering.md",
                            "rules": [{"id": i} for i in ids]}},
        "results": [{"ruleId": f["rule"], "level": "error", "message": {"text": f["message"]},
                     "locations": [{"physicalLocation": {
                         "artifactLocation": {"uri": os.path.normpath(os.path.join(prefix, f["path"]))},
                         "region": {"startLine": max(1, f["line"])}}}]} for f in findings]}]}


def cmd_check(a) -> int:
    exclude = a.exclude.split()
    c, nobj = run_check(a.root, a.rules, a.boundary_files, a.compile_db, exclude, a.denylist, a.graphviz, a.objects)
    level = "error" if a.enforce == "true" else "warning"
    for f in c.findings:
        where = os.path.normpath(os.path.join(a.annotate_prefix, f["path"]))
        print(f"{where}:{f['line']}: {f['rule']} {f['message']}")
        print(f"::{level} file={where},line={max(1, f['line'])},title={f['rule']}::{f['message']}")
    by_rule: dict[str, int] = {}
    for f in c.findings:
        by_rule[f["rule"]] = by_rule.get(f["rule"], 0) + 1
    lines = ["### Layering", "", f"{len(c.files)} file(s) under `{a.annotate_prefix or '.'}`, "
             f"{len(c.rules.zones)} zone(s), {len(c.rules.boundary)} boundary file(s), {len(c.dirs)} include "
             f"folder(s), {nobj} object(s) checked for symbols: **{len(c.findings)} finding(s)**.", ""]
    if by_rule:
        lines += ["| Rule | Findings |", "| --- | --- |"] + [f"| {k} | {v} |" for k, v in sorted(by_rule.items())]
        lines += ["", "| Where | Rule | Finding |", "| --- | --- | --- |"]
        lines += [f"| `{f['path']}:{f['line']}` | {f['rule']} | {f['message']} |" for f in c.findings[:200]]
    text = "\n".join(lines) + "\n"
    if a.summary:
        with open(a.summary, "a", encoding="utf-8") as fh:
            fh.write(text)
    if a.report_dir:
        os.makedirs(a.report_dir, exist_ok=True)
        with open(os.path.join(a.report_dir, "layering.json"), "w", encoding="utf-8") as fh:
            json.dump({"findings": c.findings, "files": len(c.files), "objects": nobj}, fh, indent=1)
        with open(os.path.join(a.report_dir, "layering.sarif"), "w", encoding="utf-8") as fh:
            json.dump(sarif(c.findings, a.annotate_prefix), fh, indent=1)
    if a.github_output:
        with open(a.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"findings={len(c.findings)}\nrules={json.dumps(sorted(by_rule))}\n")
    print(f"{len(c.findings)} finding(s) in {len(c.files)} file(s)")
    return 1 if (c.findings and a.enforce == "true") else 0


def cmd_fixtures(a) -> int:
    bad = 0
    cases = []
    good = os.path.join(a.dir, "good")
    if os.path.isdir(good):
        cases.append(("good", good, set()))
    bad_dir = os.path.join(a.dir, "bad")
    for name in sorted(os.listdir(bad_dir)) if os.path.isdir(bad_dir) else []:
        d = os.path.join(bad_dir, name)
        exp = os.path.join(d, "expect.txt")
        if not os.path.isfile(exp):
            print(f"::error file={d}::fixture {name} has no expect.txt")
            bad += 1
            continue
        with open(exp, encoding="utf-8") as fh:
            want = {w.strip() for w in fh if w.strip() and not w.startswith("#")}
        cases.append((f"bad/{name}", d, want))
    if not os.path.isdir(a.dir):
        print(f"::error::the fixtures folder {a.dir} does not exist")
        return 1
    if not cases:
        print(f"::warning::{a.dir} has neither good/ nor bad/<case>/ yet; no fixture was run")
        return 0
    for label, d, want in cases:
        rules = os.path.join(d, "rules.yml") if os.path.isfile(os.path.join(d, "rules.yml")) else a.rules
        boundary = "boundary-files.yml" if os.path.isfile(os.path.join(d, "boundary-files.yml")) else ""
        if not boundary and a.boundary_files and os.path.isfile(os.path.join(d, a.boundary_files)):
            boundary = a.boundary_files
        c, _ = run_check(d, rules, boundary, "", ["expect.txt", "rules.yml"])
        got = {f["rule"] for f in c.findings}
        ok = got == want
        print(f"{'ok  ' if ok else 'FAIL'} {label}: expected {sorted(want) or 'no finding'}, got {sorted(got) or 'none'}")
        if not ok:
            for f in c.findings:
                print(f"       {f['path']}:{f['line']}: {f['rule']} {f['message']}")
            print(f"::error file={d}::layering fixture {label}: expected {sorted(want)}, got {sorted(got)}")
            bad += 1
    return 1 if bad else 0


def cmd_poison(a) -> int:
    with open(a.rules, encoding="utf-8") as fh:
        r = yaml.safe_load(fh) or {}
    names = set()
    for p in r.get("sdk_headers") or []:
        if not any(ch in p for ch in "*?["):
            names.add(p)
            continue
        prefix = p.split("*")[0]
        for key, files in COMMON_SDK.items():
            if prefix.startswith(key) or key.startswith(prefix):
                for f in files:
                    cand = (key if key.endswith("/") else "") + f
                    if fnmatch.fnmatchcase(cand, p):
                        names.add(cand)
    os.makedirs(a.out, exist_ok=True)
    for n in sorted(names):
        path = os.path.join(a.out, n)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f'#error "{POISON_MARK}: <{n}> is an SDK or RTOS header; only a boundary file may include it"\n')
    if a.extra and os.path.isdir(a.extra):
        shutil.copytree(a.extra, a.out, dirs_exist_ok=True)
    print(f"{len(names)} poison header(s) in {a.out}" + (f", plus {a.extra}" if a.extra else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check")
    p.add_argument("--root", default=".")
    p.add_argument("--rules", required=True)
    p.add_argument("--boundary-files", default="")
    p.add_argument("--compile-db", default="")
    p.add_argument("--graphviz", default="")
    p.add_argument("--objects", default="")
    p.add_argument("--denylist", default="")
    p.add_argument("--exclude", default="")
    p.add_argument("--report-dir", default="")
    p.add_argument("--summary")
    p.add_argument("--github-output")
    p.add_argument("--annotate-prefix", default="")
    p.add_argument("--enforce", default="true", choices=["true", "false"])
    p = sub.add_parser("fixtures")
    p.add_argument("--dir", required=True)
    p.add_argument("--rules", required=True)
    p.add_argument("--boundary-files", default="")
    p = sub.add_parser("poison")
    p.add_argument("--rules", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--extra", default="")
    a = ap.parse_args()
    return {"check": cmd_check, "fixtures": cmd_fixtures, "poison": cmd_poison}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
