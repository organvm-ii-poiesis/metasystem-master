#!/usr/bin/env python3
"""Map current metasystem-master dependents and flag directory confusion."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

import tomllib

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment-specific failure
    raise SystemExit("PyYAML is required to run this script.") from exc


WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
POIESIS_ROOT = WORKSPACE_ROOT / "organvm-ii-poiesis"
METASYSTEM_ROOT = POIESIS_ROOT / "metasystem-master"
BACKPLANE_ALIASES = {
    "organvm-ii-poiesis/metasystem-master",
    "omni-dromenon-machina/metasystem-master",
}
DOCUMENTED_RUNTIME_MARKERS = {
    "/audience": "Documented Socket.io audience namespace",
    "/performer": "Documented Socket.io performer namespace",
    "localhost:3000": "Documented core-engine default port",
    "localhost:3001": "Documented performance-sdk default port",
    "redis://localhost:6379": "Documented Redis default URL",
    "PERFORMER_SECRET": "Documented performer authentication secret",
}
PRIVATE_SURFACE_PATTERNS = {
    "_archive/": "Historical archive path",
    ".meta/dependencies.json": "Stale metadata snapshot path",
    "metasystem-master/packages/": "Private workspace path reference",
}
ARCHIVED_REPO_PATTERNS = {
    "organvm-ii-poiesis/performance-sdk": "Archived standalone repo ref",
    "omni-dromenon-machina/performance-sdk": "Archived standalone repo ref",
    "organvm-ii-poiesis/core-engine": "Archived standalone repo ref",
    "omni-dromenon-machina/core-engine": "Archived standalone repo ref",
    "organvm-ii-poiesis/docs": "Archived standalone repo ref",
    "omni-dromenon-machina/docs": "Archived standalone repo ref",
    "organvm-ii-poiesis/example-generative-visual": "Archived standalone repo ref",
    "omni-dromenon-machina/example-generative-visual": "Archived standalone repo ref",
}
SKIP_DIRS = {
    ".git",
    ".next",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
}


@dataclass(frozen=True)
class Consumer:
    repo: str
    org: str
    tier: str
    promotion_status: str
    implementation_status: str
    source_file: Path
    dependency_refs: tuple[str, ...]
    archived: bool

    @property
    def lifecycle(self) -> str:
        return "archived" if self.archived else "active"


@dataclass(frozen=True)
class ConfusionSource:
    path: Path
    severity: str
    detail: str


@dataclass(frozen=True)
class TargetAssessment:
    path: Path
    dependency_files: tuple[Path, ...]
    external_dependencies: tuple[str, ...]
    backplane_packages: tuple[str, ...]
    documented_runtime_refs: tuple[str, ...]
    private_surface_refs: tuple[str, ...]
    archived_repo_refs: tuple[str, ...]
    recommendation: str
    rationale: str


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse to a mapping")
    return data


def find_workspace_packages(root: Path) -> set[str]:
    package_names: set[str] = set()
    for package_json in root.glob("packages/*/package.json"):
        data = json.loads(package_json.read_text())
        name = data.get("name")
        if isinstance(name, str):
            package_names.add(name)
    return package_names


def extract_dependency_refs(consumes: object) -> list[str]:
    refs: list[str] = []
    if not isinstance(consumes, list):
        return refs
    for item in consumes:
        if isinstance(item, dict):
            for key in ("source", "repo", "description"):
                value = item.get(key)
                if isinstance(value, str) and "metasystem-master" in value:
                    refs.append(value)
        elif isinstance(item, str) and "metasystem-master" in item:
            refs.append(item)
    return refs


def collect_consumers(root: Path) -> list[Consumer]:
    consumers: list[Consumer] = []
    for seed_path in sorted(root.glob("*/seed.yaml")):
        if seed_path.parent.name == "metasystem-master":
            continue
        data = load_yaml(seed_path)
        refs = extract_dependency_refs(data.get("consumes", []))
        if not refs:
            continue
        metadata = data.get("metadata", {})
        tier = str(metadata.get("tier", "unknown"))
        promotion_status = str(metadata.get("promotion_status", "unknown"))
        implementation_status = str(metadata.get("implementation_status", "unknown"))
        archived = (
            tier.lower() == "archive"
            or promotion_status.upper() == "ARCHIVED"
            or implementation_status.upper() == "ARCHIVED"
        )
        consumers.append(
            Consumer(
                repo=str(data.get("repo", seed_path.parent.name)),
                org=str(data.get("org", "unknown")),
                tier=tier,
                promotion_status=promotion_status,
                implementation_status=implementation_status,
                source_file=seed_path,
                dependency_refs=tuple(sorted(set(refs))),
                archived=archived,
            )
        )
    return consumers


def detect_confusion_sources(
    metasystem_root: Path, consumers: list[Consumer]
) -> list[ConfusionSource]:
    issues: list[ConfusionSource] = []

    # ecosystem.yaml is live repo metadata consumed by organvm-engine tooling.
    # It is NOT a confusion source — do not flag it here.

    dependency_snapshot = metasystem_root / ".meta" / "dependencies.json"
    if dependency_snapshot.exists():
        payload = json.loads(dependency_snapshot.read_text())
        dependent_count = len(payload.get("dependents", []))
        if dependent_count != len(consumers):
            issues.append(
                ConfusionSource(
                    path=dependency_snapshot,
                    severity="warning",
                    detail=(
                        f"Lists {dependent_count} dependents, which lags the current "
                        f"seed.yaml direct-dependent count of {len(consumers)}."
                    ),
                )
            )

    archive_deploy = metasystem_root / "_archive" / "omni-dromenon-deploy"
    if archive_deploy.exists():
        issues.append(
            ConfusionSource(
                path=archive_deploy,
                severity="warning",
                detail=(
                    "Contains a full deploy scaffold that overlaps with live "
                    "infra/, docs/, and packaged artifacts. Treat as historical only."
                ),
            )
        )

    return issues


def find_dependency_files(target_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in target_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in {
            "package.json",
            "pyproject.toml",
            "requirements.txt",
            "requirements-dev.txt",
            "docker-compose.yml",
            "Dockerfile",
            "seed.yaml",
        } or path.name.startswith("requirements-"):
            files.append(path)
    return sorted(files)


def parse_package_json(path: Path) -> set[str]:
    raw = path.read_text().strip()
    if not raw:
        return set()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return set()
    dependencies: set[str] = set()
    for key in (
        "dependencies",
        "devDependencies",
        "peerDependencies",
        "optionalDependencies",
    ):
        values = data.get(key, {})
        if isinstance(values, dict):
            dependencies.update(values.keys())
    return dependencies


def parse_pyproject(path: Path) -> set[str]:
    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError:
        return set()
    dependencies: set[str] = set()
    project = data.get("project", {})
    for value in project.get("dependencies", []):
        name = split_requirement_name(value)
        if name:
            dependencies.add(name)
    optional = project.get("optional-dependencies", {})
    if isinstance(optional, dict):
        for value_list in optional.values():
            if isinstance(value_list, list):
                for value in value_list:
                    name = split_requirement_name(value)
                    if name:
                        dependencies.add(name)
    poetry = data.get("tool", {}).get("poetry", {})
    for key in ("dependencies", "dev-dependencies"):
        values = poetry.get(key, {})
        if isinstance(values, dict):
            dependencies.update(dep for dep in values if dep != "python")
    return dependencies


def parse_requirements(path: Path) -> set[str]:
    dependencies: set[str] = set()
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-r"):
            continue
        name = split_requirement_name(line)
        if name:
            dependencies.add(name)
    return dependencies


def split_requirement_name(raw: str) -> str | None:
    candidate = raw.split(";", 1)[0].strip()
    match = re.match(r"([A-Za-z0-9_.-]+)", candidate)
    return match.group(1) if match else None


def gather_dependency_names(paths: Iterable[Path]) -> set[str]:
    dependencies: set[str] = set()
    for path in paths:
        if path.name == "package.json":
            dependencies.update(parse_package_json(path))
        elif path.name == "pyproject.toml":
            dependencies.update(parse_pyproject(path))
        elif path.name.startswith("requirements"):
            dependencies.update(parse_requirements(path))
    return dependencies


def scan_text_markers(target_root: Path, markers: dict[str, str]) -> list[str]:
    refs: list[str] = []
    text_suffixes = {
        ".cjs",
        ".cts",
        ".js",
        ".json",
        ".jsx",
        ".md",
        ".mjs",
        ".mts",
        ".py",
        ".toml",
        ".ts",
        ".tsx",
        ".txt",
        ".yaml",
        ".yml",
    }
    for path in target_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in text_suffixes and path.name not in {
            "Dockerfile",
            "docker-compose.yml",
        }:
            continue
        text = path.read_text(errors="ignore")
        for marker, description in markers.items():
            if marker in text:
                refs.append(f"{description} ({path.relative_to(target_root)})")
    return sorted(set(refs))


def resolve_target_repo(value: str) -> Path:
    candidate = Path(value).expanduser()
    if candidate.exists():
        return candidate.resolve()
    local_candidate = POIESIS_ROOT / value
    if local_candidate.exists():
        return local_candidate.resolve()
    for org_dir in WORKSPACE_ROOT.iterdir():
        if not org_dir.is_dir():
            continue
        nested_candidate = org_dir / value
        if nested_candidate.exists():
            return nested_candidate.resolve()
    raise FileNotFoundError(f"Could not resolve target repo: {value}")


def assess_target(
    target_root: Path,
    workspace_packages: set[str],
    baseline_dependencies: set[str],
) -> TargetAssessment:
    dependency_files = find_dependency_files(target_root)
    dependencies = gather_dependency_names(dependency_files)
    backplane_packages = sorted(workspace_packages.intersection(dependencies))
    documented_runtime_refs = scan_text_markers(target_root, DOCUMENTED_RUNTIME_MARKERS)
    private_surface_refs = scan_text_markers(target_root, PRIVATE_SURFACE_PATTERNS)
    archived_repo_refs = scan_text_markers(target_root, ARCHIVED_REPO_PATTERNS)

    if private_surface_refs or archived_repo_refs:
        recommendation = "major"
        rationale = (
            "Target repo references private workspace paths or archived standalone "
            "repo names, so the current backplane boundary is unstable."
        )
    elif backplane_packages:
        recommendation = "patch"
        rationale = (
            "Target repo uses existing public @omni-dromenon packages only. "
            "No version bump is required unless an API contract changes."
        )
    elif documented_runtime_refs:
        recommendation = "minor"
        rationale = (
            "Target repo couples to documented runtime behavior without depending "
            "on a versioned package, so stabilizing that contract should be tracked."
        )
    else:
        recommendation = "none"
        rationale = "No direct metasystem-master coupling was detected."

    return TargetAssessment(
        path=target_root,
        dependency_files=tuple(dependency_files),
        external_dependencies=tuple(sorted(dependencies - baseline_dependencies)),
        backplane_packages=tuple(backplane_packages),
        documented_runtime_refs=tuple(documented_runtime_refs),
        private_surface_refs=tuple(private_surface_refs),
        archived_repo_refs=tuple(archived_repo_refs),
        recommendation=recommendation,
        rationale=rationale,
    )


def build_markdown(
    consumers: list[Consumer],
    confusion_sources: list[ConfusionSource],
    target: TargetAssessment | None,
) -> str:
    generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    active_count = sum(not consumer.archived for consumer in consumers)
    archived_count = sum(consumer.archived for consumer in consumers)
    status_counts = Counter(consumer.promotion_status for consumer in consumers)

    lines = [
        "# metasystem-master Backplane Audit",
        "",
        f"Generated: {generated}",
        "",
        "## Summary",
        f"- Direct dependents from sibling `seed.yaml` files: {len(consumers)}",
        f"- Active or candidate dependents: {active_count}",
        f"- Archived dependents still pointing at the backplane: {archived_count}",
    ]
    if status_counts:
        formatted = ", ".join(
            f"{status}: {count}" for status, count in sorted(status_counts.items())
        )
        lines.append(f"- Promotion states in the current blast radius: {formatted}")
    if target is None:
        lines.append(
            "- Target repo analysis: not run. Re-run with `--target-repo <path-or-name>`."
        )
    else:
        lines.append(
            f"- Target repo analysis: `{target.path.name}` -> `{target.recommendation}`"
        )

    lines.extend(
        [
            "",
            "## Current Direct Dependents",
            "",
            "| Repo | Org | Lifecycle | Promotion | Notes |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for consumer in consumers:
        notes = "; ".join(consumer.dependency_refs)
        lines.append(
            f"| `{consumer.repo}` | `{consumer.org}` | `{consumer.lifecycle}` | "
            f"`{consumer.promotion_status}` | {notes} |"
        )

    lines.extend(["", "## Confusion Sources", ""])
    if not confusion_sources:
        lines.append("- None detected.")
    else:
        for issue in confusion_sources:
            lines.append(
                f"- `{issue.path.relative_to(METASYSTEM_ROOT)}` [{issue.severity}]: "
                f"{issue.detail}"
            )

    lines.extend(
        [
            "",
            "## Cleanup Direction",
            "",
            "- Treat `packages/`, `examples/`, `infra/`, and `docs/` as the live repo surface.",
            "- Keep historical OmniDramanon artifacts under `docs/reference/omnidramanon-cold-storage/` and out of the repo root.",
        ]
    )
    if (METASYSTEM_ROOT / "_archive").exists():
        lines.append(
            "- Treat `_archive/` as historical material only. Do not rely on it for dependency or deployment truth."
        )
    if (METASYSTEM_ROOT / ".meta" / "dependencies.json").exists():
        lines.append(
            "- Regenerate or remove `.meta/dependencies.json` if it is intended to mirror current backplane consumers."
        )
    # ecosystem.yaml is live metadata — no cleanup action needed.

    lines.extend(["", "## Target Repo Analysis", ""])
    if target is None:
        lines.append(
            "- No target repo was supplied, so version-bump analysis is intentionally omitted."
        )
    else:
        lines.append(f"- Target path: `{target.path}`")
        lines.append(f"- Recommendation: `{target.recommendation}`")
        lines.append(f"- Rationale: {target.rationale}")
        if target.dependency_files:
            lines.append(
                f"- Dependency files scanned: {', '.join(str(path.relative_to(target.path)) for path in target.dependency_files)}"
            )
        if target.external_dependencies:
            lines.append(
                f"- Dependencies not already present in the current dependent baseline: {', '.join(target.external_dependencies)}"
            )
        if target.backplane_packages:
            lines.append(
                f"- Public backplane packages consumed: {', '.join(target.backplane_packages)}"
            )
        if target.documented_runtime_refs:
            lines.append(
                f"- Documented runtime refs: {', '.join(target.documented_runtime_refs)}"
            )
        if target.private_surface_refs:
            lines.append(
                f"- Private surface refs: {', '.join(target.private_surface_refs)}"
            )
        if target.archived_repo_refs:
            lines.append(
                f"- Archived repo refs: {', '.join(target.archived_repo_refs)}"
            )

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Map metasystem-master backplane risk and directory confusion."
    )
    parser.add_argument(
        "--target-repo",
        help="Path or repo name to analyze against the metasystem-master backplane.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional Markdown output path.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional JSON output path.",
    )
    args = parser.parse_args()

    consumers = collect_consumers(POIESIS_ROOT)
    workspace_packages = find_workspace_packages(METASYSTEM_ROOT)
    confusion_sources = detect_confusion_sources(METASYSTEM_ROOT, consumers)
    baseline_files: list[Path] = []
    for consumer in consumers:
        baseline_files.extend(find_dependency_files(consumer.source_file.parent))
    baseline_dependencies = gather_dependency_names(baseline_files)

    target: TargetAssessment | None = None
    if args.target_repo:
        target = assess_target(
            resolve_target_repo(args.target_repo),
            workspace_packages,
            baseline_dependencies,
        )

    markdown = build_markdown(consumers, confusion_sources, target)

    if args.output:
        args.output.write_text(markdown)
    else:
        print(markdown)

    if args.json_output:
        payload = {
            "consumers": [
                {
                    "repo": consumer.repo,
                    "org": consumer.org,
                    "tier": consumer.tier,
                    "promotion_status": consumer.promotion_status,
                    "implementation_status": consumer.implementation_status,
                    "source_file": str(consumer.source_file),
                    "dependency_refs": list(consumer.dependency_refs),
                    "archived": consumer.archived,
                }
                for consumer in consumers
            ],
            "confusion_sources": [
                {
                    "path": str(issue.path),
                    "severity": issue.severity,
                    "detail": issue.detail,
                }
                for issue in confusion_sources
            ],
            "target": None
            if target is None
            else {
                "path": str(target.path),
                "dependency_files": [str(path) for path in target.dependency_files],
                "external_dependencies": list(target.external_dependencies),
                "backplane_packages": list(target.backplane_packages),
                "documented_runtime_refs": list(target.documented_runtime_refs),
                "private_surface_refs": list(target.private_surface_refs),
                "archived_repo_refs": list(target.archived_repo_refs),
                "recommendation": target.recommendation,
                "rationale": target.rationale,
            },
        }
        args.json_output.write_text(json.dumps(payload, indent=2) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
