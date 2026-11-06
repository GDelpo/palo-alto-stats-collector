import json
import shutil

import pandas as pd
import xmltodict
from conftest import FIXTURES, fixture_text

import device_data_collector as collector
import html_data_extractor
import main
from dataframes import read_from_csv, save_to_excel


def _device():
    results = [
        xmltodict.parse(fixture_text(name))["response"]["result"]
        for name in ("system_info.xml", "license_multiple.xml")
    ]
    return collector.create_device_from_info(results)


def test_html_preferred_versions_are_extracted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    html_dir = tmp_path / "source" / "html"
    html_dir.mkdir(parents=True)
    shutil.copy(FIXTURES / "preferred_releases.htm", html_dir / "releases.html")

    assert html_data_extractor.extract_and_process_html_tables() is True

    [json_file] = list((tmp_path / "source" / "json").glob("*.json"))
    data = json.loads(json_file.read_text())
    # Only the range between the two h2 headings; versions without a preferred row are dropped.
    assert data == [
        {
            "PAN-OS for Firewalls": {
                "11.1": ["11.1.4-h7", "20/01/2026", "Preferred"],
                "10.2": ["10.2.13-h3", "05/12/2025", "Preferred"],
            }
        }
    ]


def test_process_json_file_tries_html_once_and_stops(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    attempts = []

    def failing_extraction():
        attempts.append(1)
        return False

    monkeypatch.setattr(main, "extract_and_process_html_tables", failing_extraction)
    assert main.process_json_file(str(tmp_path / "source" / "json")) is None
    assert attempts == [1]


def test_process_json_file_stops_when_extraction_writes_nothing(tmp_path, monkeypatch):
    json_dir = tmp_path / "source" / "json"
    json_dir.mkdir(parents=True)
    (json_dir / "notes.txt").write_text("not a json")
    attempts = []
    monkeypatch.setattr(main, "extract_and_process_html_tables", lambda: attempts.append(1) or True)

    assert main.process_json_file(str(json_dir)) is None
    assert attempts == [1]


def test_preferred_version_comparison(tmp_path):
    json_file = tmp_path / "versions.json"
    json_file.write_text(
        json.dumps([{"PAN-OS for Firewalls": {"11.1": ["11.1.4-h7", "20/01/2026", "Preferred"]}}])
    )
    outdated = _device()
    current = _device()
    current.sw_version = "11.1.4-h7"

    main.update_device_with_json(str(json_file), [outdated, current])

    assert outdated.sw_version_prefered == "11.1.4-h7"
    assert current.sw_version_prefered == "is up to date with prefered version"


def test_csv_ips_are_deduplicated_in_order(tmp_path):
    csv = tmp_path / "devices.csv"
    csv.write_text("ip\n192.0.2.10\n192.0.2.11\n192.0.2.10\n")
    assert read_from_csv(csv) == ["192.0.2.10", "192.0.2.11"]


def test_excel_export_has_one_row_per_device(tmp_path):
    output = tmp_path / "output.xlsx"
    save_to_excel([_device(), _device()], str(output))

    df = pd.read_excel(output)
    assert len(df) == 2
    assert df.loc[0, "hostname"] == "fw-lab-01"
    assert df.loc[0, "license_1_feature"] == "WildFire License"
