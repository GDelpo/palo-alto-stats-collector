import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def pytest_sessionstart(session):
    # INTENTIONAL: logger.py creates ./logs when the test modules import it; move to a
    # temp dir first so tests never write into the repo. Done here, after pytest has
    # resolved testpaths, and before the test modules are collected.
    os.chdir(tempfile.mkdtemp(prefix="panos-tests-"))


# Fake settings: tests never reach a real device.
os.environ.update(USER_IP="api-user", PASSWORD_IP="s3cret-pass", PANOS_VERIFY_TLS="true")
os.environ.pop("PANOS_CA_BUNDLE", None)
os.environ["URIS"] = (
    "<show><system><info></info></system></show>|<request><license><info></info></license></request>"
)
sys.path.insert(0, str(ROOT))


def fixture_text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.exceptions.HTTPError(f"{self.status_code} error")


@pytest.fixture
def fake_device(monkeypatch):
    """Patch requests.post with a fake PAN-OS device and record every call."""
    import requests

    calls = []

    def fake_post(url, data=None, headers=None, verify=None, timeout=None):
        calls.append({"url": url, "data": data, "headers": headers or {}, "verify": verify})
        if data["type"] == "keygen":
            return FakeResponse(fixture_text("keygen.xml"))
        if "<system>" in data["cmd"]:
            return FakeResponse(fixture_text("system_info.xml"))
        return FakeResponse(fixture_text("license_single.xml"))

    monkeypatch.setattr(requests, "post", fake_post)
    return calls
