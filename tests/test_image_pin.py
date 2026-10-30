"""Dockerfile UPSTREAM_COMMIT must match docs/VENDOR-PIN.md (no docker in pytest)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN_DOC = ROOT / "docs" / "VENDOR-PIN.md"
DOCKERFILE = ROOT / "Dockerfile"


def _pin_from_vendor_doc():
    text = PIN_DOC.read_text(encoding="utf-8")
    m = re.search(r"`([0-9a-f]{40})`", text)
    assert m, "VENDOR-PIN.md must contain a 40-char commit SHA"
    return m.group(1)


def _pin_from_dockerfile():
    text = DOCKERFILE.read_text(encoding="utf-8")
    for pat in (
        r"ARG\s+UPSTREAM_COMMIT=(\S+)",
        r"ENV\s+UPSTREAM_COMMIT=(\S+)",
    ):
        m = re.search(pat, text)
        if m:
            return m.group(1).strip('"')
    raise AssertionError("Dockerfile must declare UPSTREAM_COMMIT ARG or ENV")


def test_dockerfile_pin_matches_vendor_pin_doc():
    assert _pin_from_dockerfile() == _pin_from_vendor_doc()
