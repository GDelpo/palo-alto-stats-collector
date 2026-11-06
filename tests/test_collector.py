import logging

import pytest
import requests
import xmltodict
from conftest import FakeResponse, fixture_text

import device_data_collector as collector


def _result(name):
    return xmltodict.parse(fixture_text(name))["response"]["result"]


def test_keygen_sends_credentials_in_body_not_url(fake_device):
    assert collector.generate_api_key("192.0.2.10", "api-user", "s3cret-pass") == "FAKE-API-KEY"

    call = fake_device[0]
    assert call["url"] == "https://192.0.2.10/api/"
    assert "s3cret-pass" not in call["url"]
    assert call["data"] == {"type": "keygen", "user": "api-user", "password": "s3cret-pass"}


def test_op_commands_send_key_in_header(fake_device):
    data = collector.retrieve_data_from_multiple_uris("192.0.2.10", "FAKE-API-KEY")

    assert len(data) == 2
    for call in fake_device:
        assert call["headers"] == {"X-PAN-KEY": "FAKE-API-KEY"}
        assert "FAKE-API-KEY" not in call["url"]
        assert call["data"]["type"] == "op"


def test_failed_request_never_logs_credentials(monkeypatch, caplog):
    def failing_post(url, **kwargs):
        raise requests.exceptions.ConnectionError(f"cannot reach {url}")

    monkeypatch.setattr(requests, "post", failing_post)
    with caplog.at_level(logging.ERROR, logger="error_logger"):
        assert collector.generate_api_key("192.0.2.10", "api-user", "s3cret-pass") is None
    assert "192.0.2.10" in caplog.text
    assert "s3cret-pass" not in caplog.text


def test_error_and_non_xml_responses_return_none(monkeypatch):
    monkeypatch.setattr(requests, "post", lambda url, **kw: FakeResponse(fixture_text("error.xml")))
    assert collector.post_api_request("192.0.2.10", {"type": "op", "cmd": "x"}, "k") is None

    monkeypatch.setattr(requests, "post", lambda url, **kw: FakeResponse("<html>login page"))
    assert collector.post_api_request("192.0.2.10", {"type": "op", "cmd": "x"}, "k") is None


def test_tls_verification_is_on_by_default(fake_device, monkeypatch):
    monkeypatch.delenv("PANOS_CA_BUNDLE", raising=False)
    monkeypatch.delenv("PANOS_VERIFY_TLS", raising=False)
    collector.generate_api_key("192.0.2.10", "u", "p")
    assert fake_device[-1]["verify"] is True


def test_tls_ca_bundle_and_opt_out(fake_device, monkeypatch):
    monkeypatch.setenv("PANOS_CA_BUNDLE", "/etc/ssl/panos-ca.pem")
    collector.generate_api_key("192.0.2.10", "u", "p")
    assert fake_device[-1]["verify"] == "/etc/ssl/panos-ca.pem"

    monkeypatch.delenv("PANOS_CA_BUNDLE")
    monkeypatch.setenv("PANOS_VERIFY_TLS", "false")
    collector.generate_api_key("192.0.2.10", "u", "p")
    assert fake_device[-1]["verify"] is False


@pytest.mark.parametrize(
    ("license_fixture", "expected"),
    [
        ("license_single.xml", [("Threat Prevention", "15/01/2026", False)]),
        (
            "license_multiple.xml",
            [("Threat Prevention", "15/01/2026", False), ("WildFire License", "02/03/2024", True)],
        ),
    ],
)
def test_device_parsing_with_one_or_many_licenses(license_fixture, expected):
    device = collector.create_device_from_info(
        [_result("system_info.xml"), _result(license_fixture)]
    )

    assert device.hostname == "fw-lab-01"
    assert device.model == "PA-440"
    assert device.sw_version == "11.1.2"
    assert device.identify_model() == "PAN-OS for Firewalls"
    assert [(lic.feature, lic.issued, lic.expired) for lic in device.licenses] == expected


def test_full_device_run(fake_device):
    devices = collector.process_device_list(["192.0.2.10", "192.0.2.10"])
    assert len(devices) == 2
    assert devices[0].licenses[0].feature == "Threat Prevention"


def test_missing_commands_fail_loudly(monkeypatch):
    monkeypatch.setenv("URIS", " | ")
    with pytest.raises(SystemExit):
        collector.get_commands()
