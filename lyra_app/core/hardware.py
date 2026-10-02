"""Hardware profile detection and model recommendation.

Lyra must run on modest, local machines. This module looks at what the machine
actually has (CPU, RAM, optional GPU) and maps it to a simple profile, then
recommends a local model that is realistic for that profile (VISION 20,
REQ-067, REQ-068).

Recommendations are advisory only: the user always chooses. Nothing here
downloads or installs anything.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

BASIC = "basic"
STANDARD = "standard"
ADVANCED = "advanced"

# Rough guidance per profile. Small, quantised models keep RAM use low.
_RECOMMENDATIONS = {
    BASIC: ("llama3.2:1b", "tiny models for low-RAM machines"),
    STANDARD: ("llama3.2:3b", "small models for everyday machines"),
    ADVANCED: ("llama3.1:8b", "larger models when memory allows"),
}


@dataclass
class HardwareProfile:
    """What the current machine offers, in coarse terms."""

    cpu_cores: int
    ram_gb: float
    has_gpu: bool
    profile: str

    def recommendation(self) -> str:
        return _RECOMMENDATIONS[self.profile][0]

    def reason(self) -> str:
        return _RECOMMENDATIONS[self.profile][1]


def _ram_gb() -> float:
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        return round(pages * page_size / (1024 ** 3), 1)
    except (ValueError, OSError, AttributeError):
        return 0.0


def _has_gpu() -> bool:
    if shutil.which("nvidia-smi"):
        try:
            completed = subprocess.run(
                ["nvidia-smi", "-L"], capture_output=True, text=True, timeout=3
            )
            if completed.returncode == 0 and completed.stdout.strip():
                return True
        except (OSError, subprocess.SubprocessError):
            pass
    return Path("/dev/dri").exists()


def detect() -> HardwareProfile:
    """Detect the current machine and classify it."""
    cores = os.cpu_count() or 1
    ram = _ram_gb()
    gpu = _has_gpu()

    if ram and ram < 8:
        profile = BASIC
    elif ram >= 24 or (ram >= 12 and gpu):
        profile = ADVANCED
    else:
        profile = STANDARD
    return HardwareProfile(cpu_cores=cores, ram_gb=ram, has_gpu=gpu, profile=profile)


def recommend(profile: Optional[HardwareProfile] = None) -> dict:
    """Return a recommendation dictionary for the brain and the CLI."""
    profile = profile or detect()
    return {
        "profile": profile.profile,
        "model": profile.recommendation(),
        "reason": profile.reason(),
        "cpu_cores": profile.cpu_cores,
        "ram_gb": profile.ram_gb,
        "has_gpu": profile.has_gpu,
    }
