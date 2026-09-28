import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/autosd_dashboard"))
import monitor_scenarios as scenario


def test_accepted_is_not_observed_failure():
    before = {"generation": 2, "match_count": 0}
    after = {"generation": 2, "match_count": 1, "armed": False}
    assert not scenario.observed_fault(before, after, {"status": "PASS", "packets": []})
    assert not scenario.observed_fault(before, after, {})
    assert scenario.observed_fault(before, after, {"status": "FAIL", "packets": [{"status": "TIMEOUT"}]})
    assert not scenario.observed_fault(before, dict(after, generation=3),
                                       {"status": "FAIL", "packets": [{"status": "TIMEOUT"}]})


def test_ping_report_requires_real_packet_result(tmp_path):
    (tmp_path / "console.log").write_text('HIPC start\n{"status":"FAIL","packets":[{"status":"TIMEOUT"}]}\n')
    assert scenario.ping_report(tmp_path)["packets"][0]["status"] == "TIMEOUT"


def test_opt_in_required_without_network(tmp_path):
    app = SimpleNamespace(backend="qbox-full", runtime_injection=False,
                          simulator=SimpleNamespace(collector=None), persist=lambda job: None)
    result = scenario.run(app, {"id": "test", "evidence_path": str(tmp_path)}, io.BytesIO())
    assert result["status"] == "UNSUPPORTED"
    assert not result["recovery_required"]
    assert json.loads((tmp_path / "scenarios.json").read_text())["status"] == "UNSUPPORTED"


def test_mutation_timeout_unknown_and_never_retried(monkeypatch):
    calls = []
    class Connection:
        def __init__(self, *args, **kwargs):
            pass
        def request(self, *args, **kwargs):
            calls.append(args)
            raise TimeoutError("test")
        def close(self):
            pass
    monkeypatch.setattr(scenario.http.client, "HTTPConnection", Connection)
    monkeypatch.setattr(scenario, "verify_listener", lambda *args: None)
    collector = SimpleNamespace(_get=lambda path: {}, timeout=.1, max_body=1024,
        endpoint={"host": "127.0.0.1", "port": 18080, "owner_pid": 1, "owner_start_ticks": 2})
    with pytest.raises(scenario.UnknownOutcome):
        scenario.request(collector, "POST", "/api/v1/injections",
                         {"target": scenario.MHU, "action": "drop-next-doorbell"})
    assert len(calls) == 1


def test_arbitrary_mutation_rejected():
    with pytest.raises(ValueError):
        scenario.request(None, "POST", "/api/v1/injections", {"target": "anything", "action": "write"})


def test_full_reset_requires_every_domain_epoch_advance():
    domains = ["rse", "si-cl0", "si-cl1", "ap"]
    before = {"domains": [{"id": domain, "boot_epoch": 1} for domain in domains]}
    after = {"domains": [{"id": domain, "boot_epoch": 2} for domain in domains]}
    assert scenario.all_domain_epochs_advanced(before, after)
    for retained in domains:
        mixed = {"domains": [{"id": domain, "boot_epoch": 1 if domain == retained else 2}
                             for domain in domains]}
        assert not scenario.all_domain_epochs_advanced(before, mixed)
    assert not scenario.all_domain_epochs_advanced(before, {"domains": after["domains"][:3]})
    assert not scenario.all_domain_epochs_advanced({}, after)
    assert not scenario.all_domain_epochs_advanced({"domains": [{"id": d, "boot_epoch": True} for d in domains]}, after)
