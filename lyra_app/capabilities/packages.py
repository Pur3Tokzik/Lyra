"""Capability packages: install, export and load third-party capabilities.

A capability package is either a folder or a ``.lyra-capability`` file (a zip)
containing a ``capability.json`` manifest and a Python module that builds the
capability. Installing copies it into the instance's ``modules/`` folder, so the
capability travels with the companion.

Security rules (``docs/CAPABILITY_SECURITY.md``):
- the manifest is validated *before* any module is imported;
- nothing is installed or enabled silently;
- permissions must be granted before a capability with permissions runs;
- installation is local only: no network, no remote registry in this phase.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from lyra_app.capabilities.base import BaseCapability
from lyra_app.capabilities.metadata import CapabilityMetadata

MANIFEST_NAME = "capability.json"
PACKAGE_SUFFIX = ".lyra-capability"
_MODULES_DIR = "modules"


class PackageError(ValueError):
    """Raised when a package is missing, malformed or unsafe."""


@dataclass(frozen=True)
class CapabilityManifest:
    """The declared contents of a capability package."""

    name: str
    version: str
    description: str
    entry: str
    factory: str = "create"
    author: str = "unknown"
    permissions: Tuple[str, ...] = ()
    requirements: Tuple[str, ...] = ()
    trust: str = "community"

    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            permissions=self.permissions,
            requirements=self.requirements,
            trust=self.trust,
        )


@dataclass
class InstalledPackage:
    """A package found inside the instance's modules folder."""

    manifest: CapabilityManifest
    root: Path
    capability: BaseCapability = field(default=None)  # type: ignore[assignment]


def _parse_manifest(data: dict, where: str) -> CapabilityManifest:
    required = ("name", "version", "description", "entry")
    missing = [key for key in required if not str(data.get(key, "")).strip()]
    if missing:
        raise PackageError(f"{where}: missing manifest field(s): {', '.join(missing)}")
    entry = str(data["entry"])
    if entry.startswith("/") or ".." in Path(entry).parts:
        raise PackageError(f"{where}: entry must stay inside the package")
    if not entry.endswith(".py"):
        raise PackageError(f"{where}: entry must be a .py file")
    return CapabilityManifest(
        name=str(data["name"]).strip(),
        version=str(data["version"]).strip(),
        description=str(data["description"]).strip(),
        entry=entry,
        factory=str(data.get("factory", "create")).strip() or "create",
        author=str(data.get("author", "unknown")),
        permissions=tuple(data.get("permissions", [])),
        requirements=tuple(data.get("requirements", [])),
        trust=str(data.get("trust", "community")),
    )


def read_manifest(source: Path | str) -> Tuple[CapabilityManifest, Path]:
    """Read and validate a manifest from a folder or a zip package."""
    source = Path(source)
    if not source.exists():
        raise PackageError(f"not found: {source}")
    if source.is_dir():
        manifest_path = source / MANIFEST_NAME
        if not manifest_path.exists():
            raise PackageError(f"{source}: no {MANIFEST_NAME}")
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except ValueError as error:
            raise PackageError(f"{source}: invalid JSON: {error}") from error
        return _parse_manifest(data, str(source)), source
    if zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            if MANIFEST_NAME not in archive.namelist():
                raise PackageError(f"{source}: no {MANIFEST_NAME} in archive")
            data = json.loads(archive.read(MANIFEST_NAME).decode("utf-8"))
        return _parse_manifest(data, str(source)), source
    raise PackageError(f"{source}: not a folder or a {PACKAGE_SUFFIX} file")


def _modules_dir(home: Path | str) -> Path:
    return Path(home) / _MODULES_DIR


def install(home: Path | str, source: Path | str) -> CapabilityManifest:
    """Copy a package into the instance's modules folder. Local only."""
    manifest, root = read_manifest(source)
    destination = _modules_dir(home) / manifest.name
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if root.is_dir():
        shutil.copytree(root, destination)
    else:
        with zipfile.ZipFile(root) as archive:
            for member in archive.namelist():
                target = (destination / member).resolve()
                if not str(target).startswith(str(destination.resolve())):
                    raise PackageError(f"{root}: archive escapes the package")
            archive.extractall(destination)
    # The manifest must still validate once unpacked.
    read_manifest(destination)
    return manifest


def remove(home: Path | str, name: str) -> bool:
    """Delete an installed package. Refuses to leave the modules folder."""
    if "/" in name or ".." in name:
        return False
    destination = _modules_dir(home) / name
    if not destination.is_dir():
        return False
    shutil.rmtree(destination)
    return True


def installed_packages(home: Path | str) -> List[Tuple[CapabilityManifest, Path]]:
    """Every valid package currently in the modules folder, sorted by name."""
    folder = _modules_dir(home)
    if not folder.is_dir():
        return []
    found: List[Tuple[CapabilityManifest, Path]] = []
    for child in sorted(folder.iterdir()):
        if not child.is_dir():
            continue
        try:
            manifest, _ = read_manifest(child)
        except PackageError:
            continue  # a broken package is skipped, never loaded
        found.append((manifest, child))
    return found


def load_capability(manifest: CapabilityManifest, root: Path) -> BaseCapability:
    """Import a package module and call its factory. Raises PackageError on failure."""
    module_path = (root / manifest.entry).resolve()
    if not module_path.exists() or root.resolve() not in module_path.parents:
        raise PackageError(f"{manifest.name}: entry not inside the package")
    spec = importlib.util.spec_from_file_location(f"lyra_cap_{manifest.name}", module_path)
    if spec is None or spec.loader is None:
        raise PackageError(f"{manifest.name}: cannot load {manifest.entry}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as error:  # noqa: BLE001 - a bad package must not crash core
        raise PackageError(f"{manifest.name}: import failed: {error}") from error
    factory = getattr(module, manifest.factory, None)
    if not callable(factory):
        raise PackageError(f"{manifest.name}: no callable '{manifest.factory}' in {manifest.entry}")
    try:
        capability = factory()
    except Exception as error:  # noqa: BLE001
        raise PackageError(f"{manifest.name}: factory failed: {error}") from error
    if not isinstance(capability, BaseCapability):
        raise PackageError(f"{manifest.name}: factory did not return a capability")
    return capability


def export(home: Path | str, name: str, destination: Path | str) -> Path:
    """Package an installed capability into a shareable zip for the community."""
    if "/" in name or ".." in name:
        raise PackageError(f"invalid name: {name}")
    source = _modules_dir(home) / name
    manifest, _ = read_manifest(source)
    destination = Path(destination)
    if destination.is_dir():
        destination = destination / f"{manifest.name}-{manifest.version}{PACKAGE_SUFFIX}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source).as_posix())
    return destination
