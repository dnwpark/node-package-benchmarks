#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.14"
# dependencies = ["PyYAML>=6.0"]
# ///
"""
Parse lockfiles for every repo under ./repos/ and write
./dependencies/{repo}.json with the full list of packages.

Fields per package
------------------
name            str
version         str
direct          bool  – True when listed in the root package.json
scope           str   – prod | dev | optional | peer | unknown
specifier       str?  – version range from package.json (direct only)
resolved        str?  – registry URL
integrity       str?  – sha512 / sha1 hash
engines         obj?
os              str | list?
cpu             str | list?
deprecated      str?
bundled         bool?
hasBin          bool?
platformSpecific bool? – vlt type-3 (native optional binaries)
resolution      str?  – yarn berry
checksum        str?  – yarn berry
languageName    str?  – yarn berry
linkType        str?  – yarn berry

Supported lockfiles
-------------------
npm   package-lock.json  v1 / v2 / v3
pnpm  pnpm-lock.yaml     v5.3 / v5.4 / v6.0 / v6.1 / v9.0
yarn  yarn.lock          classic v1 + berry (v3 / v4)
bun   bun.lock           text  (lockfileVersion 1)
      bun.lockb          binary – noted, not parsed
vlt   vlt-lock.json
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Required, TypedDict

import yaml

REPOS_DIR = Path(__file__).parent / "repos"
DEPS_DIR = Path(__file__).parent / "dependencies"

Obj = dict[str, Any]


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------


class PackageEntry(TypedDict, total=False):
    name: Required[str]
    version: Required[str]
    direct: Required[bool]
    scope: Required[str]
    specifier: str
    resolved: str
    integrity: str
    engines: dict[str, str]
    os: str | list[str]
    cpu: str | list[str]
    deprecated: str
    bundled: bool
    hasBin: bool
    platformSpecific: bool
    resolution: str
    checksum: str
    languageName: str
    linkType: str


class RepoResult(TypedDict, total=False):
    repo: Required[str]
    packageManager: Required[str]
    packages: Required[list[PackageEntry]]
    lockfile: str | None
    lockfileVersion: str | None
    note: str
    error: str
    yarnFlavour: str
    yarnToolVersion: str | None


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def parse_jsonc(text: str) -> Any:
    """
    JSONC parser: strips // and /* */ comments (string-aware)
    then removes trailing commas before ] or }.
    """
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == '"':
            out.append(ch)
            i += 1
            while i < n:
                c = text[i]
                out.append(c)
                i += 1
                if c == "\\":
                    if i < n:
                        out.append(text[i])
                        i += 1
                elif c == '"':
                    break
        elif ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i < n and not (
                text[i] == "*" and i + 1 < n and text[i + 1] == "/"
            ):
                i += 1
            i += 2
        else:
            out.append(ch)
            i += 1
    cleaned = re.sub(r",(\s*[}\]])", r"\1", "".join(out))
    return json.loads(cleaned)


def read_pkg(repo: Path) -> Obj:
    p = repo / "package.json"
    return json.loads(p.read_text("utf-8")) if p.exists() else {}


@dataclass
class ScopeMaps:
    prod: set[str] = field(default_factory=set)
    dev: set[str] = field(default_factory=set)
    optional: set[str] = field(default_factory=set)
    peer: set[str] = field(default_factory=set)
    all_pkgs: set[str] = field(default_factory=set)
    specifiers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_pkg(cls, pkg: Obj) -> ScopeMaps:
        def _keys(section: str) -> set[str]:
            v = pkg.get(section, {})
            return set(v) if isinstance(v, dict) else set()

        prod = _keys("dependencies")
        dev = _keys("devDependencies")
        optional = _keys("optionalDependencies")
        peer = _keys("peerDependencies")

        specs: dict[str, str] = {}
        for sec in (
            "dependencies",
            "devDependencies",
            "optionalDependencies",
            "peerDependencies",
        ):
            d = pkg.get(sec, {})
            if isinstance(d, dict):
                for k, v in d.items():
                    if isinstance(k, str) and isinstance(v, str):
                        specs[k] = v

        return cls(
            prod=prod,
            dev=dev,
            optional=optional,
            peer=peer,
            all_pkgs=prod | dev | optional | peer,
            specifiers=specs,
        )

    def scope_of(self, name: str) -> str:
        if name in self.dev:
            return "dev"
        if name in self.optional:
            return "optional"
        if name in self.peer:
            return "peer"
        return "prod"


def clean_ver(v: str) -> str:
    """Strip pnpm peer-resolution suffixes (_peer@1 or (peer@1))."""
    return v.split("_")[0].split("(")[0]


def _s(d: Obj, *keys: str) -> str | None:
    """Return d[k1][k2]... if it is a str, else None."""
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur if isinstance(cur, str) else None


def _d(d: Obj, key: str) -> Obj:
    v = d.get(key)
    return v if isinstance(v, dict) else {}


def _b(d: Obj, key: str) -> bool:
    return bool(d.get(key))


def _attach(e: PackageEntry, info: Obj) -> None:
    """Copy common optional fields from a lockfile entry dict."""
    if v := _s(info, "resolved"):
        e["resolved"] = v
    if v := _s(info, "integrity"):
        e["integrity"] = v
    eng = _d(info, "engines")
    if eng:
        e["engines"] = {k: str(v) for k, v in eng.items() if isinstance(k, str)}
    if (o := info.get("os")) is not None:
        e["os"] = o
    if (c := info.get("cpu")) is not None:
        e["cpu"] = c
    if dep := _s(info, "deprecated"):
        e["deprecated"] = dep
    if _b(info, "hasBin"):
        e["hasBin"] = True
    if _b(info, "inBundle"):
        e["bundled"] = True


# ---------------------------------------------------------------------------
# npm  (package-lock.json  v1 / v2 / v3)
# ---------------------------------------------------------------------------


def _npm_v1(repo: Path, lock: Obj) -> list[PackageEntry]:
    maps = ScopeMaps.from_pkg(read_pkg(repo))
    pkgs: list[PackageEntry] = []

    def walk(deps: Obj) -> None:
        for name, info in deps.items():
            if not isinstance(info, dict):
                continue
            is_direct = name in maps.all_pkgs
            scope = (
                maps.scope_of(name)
                if is_direct
                else (
                    "dev"
                    if _b(info, "dev")
                    else "optional" if _b(info, "optional") else "prod"
                )
            )
            e: PackageEntry = {
                "name": name,
                "version": _s(info, "version") or "",
                "direct": is_direct,
                "scope": scope,
            }
            if is_direct and (sp := maps.specifiers.get(name)):
                e["specifier"] = sp
            _attach(e, info)
            pkgs.append(e)
            if nested := _d(info, "dependencies"):
                walk(nested)

    walk(_d(lock, "dependencies"))
    return pkgs


def _npm_v2v3(lock: Obj) -> list[PackageEntry]:
    root = _d(lock, "packages").get("", {})
    if not isinstance(root, dict):
        root = {}
    dp = _d(root, "dependencies")
    dd = _d(root, "devDependencies")
    do_ = _d(root, "optionalDependencies")
    dpeer = _d(root, "peerDependencies")
    direct_all = set(dp) | set(dd) | set(do_) | set(dpeer)
    direct_specs: dict[str, str] = {
        **{k: v for k, v in dp.items() if isinstance(v, str)},
        **{k: v for k, v in dd.items() if isinstance(v, str)},
        **{k: v for k, v in do_.items() if isinstance(v, str)},
        **{k: v for k, v in dpeer.items() if isinstance(v, str)},
    }

    pkgs: list[PackageEntry] = []
    for pkg_path, info in _d(lock, "packages").items():
        if pkg_path == "" or not isinstance(info, dict):
            continue
        # Extract innermost name from  node_modules/@scope/foo
        m = re.search(
            r"(?:^|.*/)node_modules/(@[^/]+/[^/]+|[^/]+)$",
            pkg_path,
        )
        if not m:
            continue
        name = m.group(1)
        is_direct = name in direct_all
        scope = (
            (
                "dev"
                if name in dd
                else (
                    "optional"
                    if name in do_
                    else "peer" if name in dpeer else "prod"
                )
            )
            if is_direct
            else (
                "dev"
                if _b(info, "dev")
                else (
                    "optional"
                    if _b(info, "optional")
                    else "peer" if _b(info, "peer") else "prod"
                )
            )
        )
        e: PackageEntry = {
            "name": name,
            "version": _s(info, "version") or "",
            "direct": is_direct,
            "scope": scope,
        }
        if is_direct and (sp := direct_specs.get(name)):
            e["specifier"] = sp
        _attach(e, info)
        if lic := _s(info, "license"):
            e["resolved"] = e.get("resolved", "")  # keep order
            # store licence separately – reuse resolved slot isn't right;
            # PackageEntry has no licence field, skip silently
            _ = lic
        pkgs.append(e)
    return pkgs


def parse_npm(repo: Path) -> RepoResult:
    raw = (repo / "package-lock.json").read_text("utf-8")
    lock: Obj = json.loads(raw)
    ver = int(lock.get("lockfileVersion", 1))
    pkgs = _npm_v1(repo, lock) if ver == 1 else _npm_v2v3(lock)
    return {
        "repo": repo.name,
        "packageManager": "npm",
        "lockfile": "package-lock.json",
        "lockfileVersion": str(ver),
        "packages": pkgs,
    }


# ---------------------------------------------------------------------------
# pnpm  (pnpm-lock.yaml  v5.3 / v5.4 / v6.0 / v6.1 / v9.0)
# ---------------------------------------------------------------------------


def _pnpm_load(repo: Path) -> Obj:
    content = (repo / "pnpm-lock.yaml").read_text("utf-8")
    docs: list[Any] = list(yaml.safe_load_all(content))
    # Some repos (e.g. pnpm itself) use a two-document lockfile
    lock = next(
        (d for d in docs if isinstance(d, dict) and "lockfileVersion" in d),
        docs[0] if docs else {},
    )
    return lock if isinstance(lock, dict) else {}


def _pnpm_v5(lock: Obj) -> list[PackageEntry]:
    specs = _d(lock, "specifiers")
    dp = _d(lock, "dependencies")
    dd = _d(lock, "devDependencies")
    do_ = _d(lock, "optionalDependencies")
    direct_prod = set(dp)
    direct_dev = set(dd)
    direct_opt = set(do_)
    direct_all = direct_prod | direct_dev | direct_opt

    pkgs: list[PackageEntry] = []
    for raw_key, info in _d(lock, "packages").items():
        if not isinstance(info, dict):
            continue
        # Key:  /name/version  or  /@scope/name/version
        key = raw_key.lstrip("/")
        if key.startswith("@"):
            parts = key.split("/")
            name = parts[0] + "/" + parts[1]
            ver_str = "/".join(parts[2:])
        else:
            idx = key.index("/")
            name, ver_str = key[:idx], key[idx + 1 :]
        version = clean_ver(ver_str)

        is_direct = name in direct_all
        scope = (
            (
                "dev"
                if name in direct_dev
                else "optional" if name in direct_opt else "prod"
            )
            if is_direct
            else (
                "dev"
                if _b(info, "dev")
                else (
                    "optional"
                    if _b(info, "optional")
                    else "peer" if _b(info, "peer") else "prod"
                )
            )
        )
        e: PackageEntry = {
            "name": name,
            "version": version,
            "direct": is_direct,
            "scope": scope,
        }
        if is_direct and (sp := _s(specs, name)):
            e["specifier"] = sp
        res = info.get("resolution")
        if isinstance(res, dict):
            if v := _s(res, "integrity"):
                e["integrity"] = v
            if v := _s(res, "tarball"):
                e["resolved"] = v
        if eng := _d(info, "engines"):
            e["engines"] = {
                k: str(v) for k, v in eng.items() if isinstance(k, str)
            }
        if dep := _s(info, "deprecated"):
            e["deprecated"] = dep
        if _b(info, "hasBin"):
            e["hasBin"] = True
        pkgs.append(e)
    return pkgs


def _pnpm_v6plus(lock: Obj) -> list[PackageEntry]:
    root_imp = _d(_d(lock, "importers"), ".")
    dp = _d(root_imp, "dependencies")
    dd = _d(root_imp, "devDependencies")
    do_ = _d(root_imp, "optionalDependencies")
    direct_dev = set(dd)
    direct_opt = set(do_)
    direct_all = set(dp) | direct_dev | direct_opt
    all_direct_info: Obj = {**dp, **dd, **do_}

    # Build base-name → scope from snapshots (best-effort)
    snap_scope: dict[str, str] = {}
    for sk, sv in _d(lock, "snapshots").items():
        base = sk.split("(")[0]
        if isinstance(sv, dict):
            if _b(sv, "dev"):
                snap_scope[base] = "dev"
            elif _b(sv, "optional"):
                snap_scope[base] = "optional"

    pkgs: list[PackageEntry] = []
    for raw_key, info in _d(lock, "packages").items():
        if not isinstance(info, dict):
            continue
        # Key: name@version  (last @ separates name from version)
        at = raw_key.rfind("@", 1)
        name = raw_key[:at]
        version = clean_ver(raw_key[at + 1 :])

        is_direct = name in direct_all
        scope = (
            (
                "dev"
                if name in direct_dev
                else "optional" if name in direct_opt else "prod"
            )
            if is_direct
            else snap_scope.get(raw_key, "prod")
        )
        e: PackageEntry = {
            "name": name,
            "version": version,
            "direct": is_direct,
            "scope": scope,
        }
        if is_direct:
            entry_info = all_direct_info.get(name)
            if isinstance(entry_info, dict):
                if sp := _s(entry_info, "specifier"):
                    e["specifier"] = sp
        res = info.get("resolution")
        if isinstance(res, dict):
            if v := _s(res, "integrity"):
                e["integrity"] = v
            if v := _s(res, "tarball"):
                e["resolved"] = v
        if eng := _d(info, "engines"):
            e["engines"] = {
                k: str(v) for k, v in eng.items() if isinstance(k, str)
            }
        if dep := _s(info, "deprecated"):
            e["deprecated"] = dep
        if _b(info, "hasBin"):
            e["hasBin"] = True
        pkgs.append(e)
    return pkgs


def parse_pnpm(repo: Path) -> RepoResult:
    lock = _pnpm_load(repo)
    raw_ver = lock.get("lockfileVersion", "")
    lock_ver = str(raw_ver)
    ver_num = float(lock_ver) if lock_ver else 0.0
    pkgs = _pnpm_v5(lock) if ver_num < 6 else _pnpm_v6plus(lock)
    return {
        "repo": repo.name,
        "packageManager": "pnpm",
        "lockfile": "pnpm-lock.yaml",
        "lockfileVersion": lock_ver,
        "packages": pkgs,
    }


# ---------------------------------------------------------------------------
# yarn v1  (yarn.lock  classic)
# ---------------------------------------------------------------------------


def _yarn_v1_name(header: str) -> str:
    """
    "react@^18, react@^17":  →  react
    @scope/pkg@^1.0:         →  @scope/pkg
    """
    clean = header.strip().strip('"').split(",")[0].strip()
    at = clean.rfind("@", 1)
    return clean[:at] if at > 0 else clean


def parse_yarn_v1(repo: Path) -> RepoResult:
    lines = (repo / "yarn.lock").read_text("utf-8").splitlines()
    maps = ScopeMaps.from_pkg(read_pkg(repo))
    seen: set[str] = set()
    pkgs: list[PackageEntry] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        # Header: non-indented, non-comment, ends with colon
        if line and not line[0] in " \t#" and line.endswith(":"):
            name = _yarn_v1_name(line[:-1])
            entry: dict[str, str] = {}
            i += 1
            # Collect 2-space-indented key-value lines
            while i < len(lines) and lines[i].startswith("  "):
                body = lines[i].strip()
                if body.startswith("version "):
                    entry["version"] = body[8:].strip().strip('"')
                elif body.startswith("resolved "):
                    entry["resolved"] = (
                        body[9:].strip().strip('"').split("#")[0]
                    )
                elif body.startswith("integrity "):
                    entry["integrity"] = body[10:].strip()
                i += 1
                # Skip 4-space sub-blocks (dependencies etc.)
                while i < len(lines) and lines[i].startswith("    "):
                    i += 1
            ver = entry.get("version", "")
            key = f"{name}@{ver}"
            if ver and key not in seen:
                seen.add(key)
                is_direct = name in maps.all_pkgs
                scope = maps.scope_of(name) if is_direct else "unknown"
                e: PackageEntry = {
                    "name": name,
                    "version": ver,
                    "direct": is_direct,
                    "scope": scope,
                }
                if is_direct and (sp := maps.specifiers.get(name)):
                    e["specifier"] = sp
                if r := entry.get("resolved"):
                    e["resolved"] = r
                if h := entry.get("integrity"):
                    e["integrity"] = h
                pkgs.append(e)
        else:
            i += 1

    return {
        "repo": repo.name,
        "packageManager": "yarn",
        "lockfile": "yarn.lock",
        "lockfileVersion": "1",
        "yarnFlavour": "classic",
        "packages": pkgs,
    }


# ---------------------------------------------------------------------------
# yarn berry  (yarn.lock  __metadata block present)
# ---------------------------------------------------------------------------


def _berry_name(header: str) -> str:
    """
    "@scope/pkg@npm:^1.0, @scope/pkg@npm:^1.1":  →  @scope/pkg
    """
    clean = header.strip().strip('"').split(",")[0].strip()
    at = clean.rfind("@", 1)
    return clean[:at] if at > 0 else clean


def _berry_tool_version(repo: Path) -> str | None:
    rc = repo / ".yarnrc.yml"
    if not rc.exists():
        return None
    text = rc.read_text("utf-8")
    m = re.search(r"yarnPath:\s*\.yarn/releases/yarn-([^\s]+)\.cjs", text)
    if m:
        return m.group(1)
    m = re.search(r'packageManager:\s*["\']?yarn@([^\s"\']+)', text)
    return m.group(1) if m else None


def parse_yarn_berry(repo: Path) -> RepoResult:
    content = (repo / "yarn.lock").read_text("utf-8")
    lines = content.splitlines()
    maps = ScopeMaps.from_pkg(read_pkg(repo))

    m = re.search(r"__metadata:\s*\n\s+version:\s*(\d+)", content)
    meta_ver = int(m.group(1)) if m else None

    seen: set[str] = set()
    pkgs: list[PackageEntry] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if (
            line
            and not line[0] in " \t#"
            and line.endswith(":")
            and not line.startswith("__metadata")
        ):
            name = _berry_name(line[:-1])
            entry: dict[str, str] = {}
            i += 1
            while i < len(lines) and (
                lines[i].startswith("  ") or lines[i].startswith("\t")
            ):
                body = lines[i].strip()
                for prefix, field_name in (
                    ("version:", "version"),
                    ("resolution:", "resolution"),
                    ("checksum:", "checksum"),
                    ("languageName:", "languageName"),
                    ("linkType:", "linkType"),
                ):
                    if body.startswith(prefix):
                        entry[field_name] = (
                            body[len(prefix) :].strip().strip('"')
                        )
                        break
                i += 1
                # Skip 4-space sub-blocks
                while i < len(lines) and (
                    lines[i].startswith("    ") or lines[i].startswith("\t\t")
                ):
                    i += 1
            ver = entry.get("version", "")
            key = f"{name}@{ver}"
            if ver and name and name != "__metadata" and key not in seen:
                seen.add(key)
                is_direct = name in maps.all_pkgs
                scope = maps.scope_of(name) if is_direct else "unknown"
                e: PackageEntry = {
                    "name": name,
                    "version": ver,
                    "direct": is_direct,
                    "scope": scope,
                }
                if is_direct and (sp := maps.specifiers.get(name)):
                    e["specifier"] = sp
                for fk in (
                    "resolution",
                    "checksum",
                    "languageName",
                    "linkType",
                ):
                    if fv := entry.get(fk):
                        e[fk] = fv
                pkgs.append(e)
        elif line.startswith("__metadata"):
            i += 1
            while i < len(lines) and (
                lines[i].startswith("  ") or lines[i].startswith("\t")
            ):
                i += 1
        else:
            i += 1

    return {
        "repo": repo.name,
        "packageManager": "yarn",
        "lockfile": "yarn.lock",
        "lockfileVersion": f"berry-metadata-v{meta_ver}",
        "yarnFlavour": "berry",
        "yarnToolVersion": _berry_tool_version(repo),
        "packages": pkgs,
    }


# ---------------------------------------------------------------------------
# bun text  (bun.lock  lockfileVersion 1)
# ---------------------------------------------------------------------------


def parse_bun_text(repo: Path) -> RepoResult:
    lock: Any = parse_jsonc((repo / "bun.lock").read_text("utf-8"))
    workspaces = lock.get("workspaces", {})
    root_ws: Any = workspaces.get("") or (
        next(iter(workspaces.values()), {}) if workspaces else {}
    )
    root_ws = root_ws if isinstance(root_ws, dict) else {}
    maps = ScopeMaps.from_pkg(root_ws)

    pkgs: list[PackageEntry] = []
    for pkg_name, info in (lock.get("packages") or {}).items():
        if not isinstance(info, list):
            continue
        # info: [resolutionStr, extra?, metadata?, integrity?]
        res_str = info[0] if info and isinstance(info[0], str) else ""
        metadata = next((x for x in info if isinstance(x, dict)), None)
        integrity = next(
            (x for x in info if isinstance(x, str) and re.match(r"sha\d+-", x)),
            None,
        )
        at = res_str.rfind("@")
        version = res_str[at + 1 :] if at >= 0 else ""

        is_direct = pkg_name in maps.all_pkgs
        scope = maps.scope_of(pkg_name) if is_direct else "unknown"
        e: PackageEntry = {
            "name": pkg_name,
            "version": version,
            "direct": is_direct,
            "scope": scope,
        }
        if is_direct and (sp := maps.specifiers.get(pkg_name)):
            e["specifier"] = sp
        if integrity:
            e["integrity"] = integrity
        if metadata:
            if eng := metadata.get("engines"):
                if isinstance(eng, dict):
                    e["engines"] = {
                        k: str(v) for k, v in eng.items() if isinstance(k, str)
                    }
            for fk in ("os", "cpu"):
                if (fv := metadata.get(fk)) is not None:
                    e[fk] = fv
            if dep := metadata.get("deprecated"):
                if isinstance(dep, str):
                    e["deprecated"] = dep
        pkgs.append(e)

    return {
        "repo": repo.name,
        "packageManager": "bun",
        "lockfile": "bun.lock",
        "lockfileVersion": str(lock.get("lockfileVersion", 1)),
        "packages": pkgs,
    }


# ---------------------------------------------------------------------------
# vlt  (vlt-lock.json)
# ---------------------------------------------------------------------------


def parse_vlt(repo: Path) -> RepoResult:
    lock: Obj = json.loads((repo / "vlt-lock.json").read_text("utf-8"))
    maps = ScopeMaps.from_pkg(read_pkg(repo))
    pkgs: list[PackageEntry] = []

    for node_key, info in lock.get("nodes", {}).items():
        # Key: ··@scope§name@version  (§ = / , ·· = path prefix)
        normalized = node_key.removeprefix("··").replace("§", "/")
        at = normalized.rfind("@", 1)
        name = normalized[:at] if at > 0 else normalized
        version = normalized[at + 1 :] if at > 0 else ""

        dep_type = info[0] if isinstance(info, list) and info else None
        if dep_type == 1:  # root node
            continue
        integrity = (
            info[2]
            if isinstance(info, list)
            and len(info) > 2
            and isinstance(info[2], str)
            else None
        )

        is_direct = name in maps.all_pkgs
        scope = maps.scope_of(name) if is_direct else "unknown"
        e: PackageEntry = {
            "name": name,
            "version": version,
            "direct": is_direct,
            "scope": scope,
        }
        if is_direct and (sp := maps.specifiers.get(name)):
            e["specifier"] = sp
        if integrity:
            e["integrity"] = integrity
        if dep_type == 3:
            e["platformSpecific"] = True
        pkgs.append(e)

    return {
        "repo": repo.name,
        "packageManager": "vlt",
        "lockfile": "vlt-lock.json",
        "lockfileVersion": None,
        "packages": pkgs,
    }


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def parse_repo(repo: Path) -> RepoResult:
    def has(name: str) -> bool:
        return (repo / name).exists()

    try:
        if has("bun.lockb"):
            return {
                "repo": repo.name,
                "packageManager": "bun",
                "lockfile": "bun.lockb",
                "lockfileVersion": None,
                "note": ("Binary format — cannot be parsed without bun CLI"),
                "packages": [],
            }
        if has("package-lock.json"):
            return parse_npm(repo)
        if has("pnpm-lock.yaml"):
            return parse_pnpm(repo)
        if has("yarn.lock"):
            text = (repo / "yarn.lock").read_text("utf-8")
            return (
                parse_yarn_berry(repo)
                if "__metadata:" in text
                else parse_yarn_v1(repo)
            )
        if has("bun.lock"):
            return parse_bun_text(repo)
        if has("vlt-lock.json"):
            return parse_vlt(repo)
        return {
            "repo": repo.name,
            "packageManager": "unknown",
            "lockfile": None,
            "note": "No recognised lockfile found",
            "packages": [],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "repo": repo.name,
            "packageManager": "unknown",
            "lockfile": None,
            "error": str(exc),
            "packages": [],
        }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    DEPS_DIR.mkdir(parents=True, exist_ok=True)
    repos = sorted(p for p in REPOS_DIR.iterdir() if p.is_dir())
    if not repos:
        print(f"No repos found under {REPOS_DIR}", file=sys.stderr)
        return 1

    ok = skipped = failed = 0
    for repo in repos:
        print(f"  {repo.name} … ", end="", flush=True)
        result = parse_repo(repo)
        out = DEPS_DIR / f"{repo.name}.json"
        out.write_text(json.dumps(result, indent=2), "utf-8")

        if "error" in result:
            print(f"FAIL  {result['error']}")
            failed += 1
        elif "note" in result:
            print(f"SKIP  {result['note']}")
            skipped += 1
        else:
            print(f"ok    {len(result['packages'])} packages")
            ok += 1

    print(f"\n{ok} ok, {skipped} skipped, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
