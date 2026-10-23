"""Lifecycle failures must retain cleanup and fresh generations."""

from types import SimpleNamespace
from unittest.mock import Mock
import json
from urllib.request import urlopen

import pytest

from test_automation import pytest_plugin as plugin


def test_start_failure_stops_device_and_disconnects(monkeypatch):
    bundle = SimpleNamespace(driver=Mock(), manager=Mock(), login_primary=Mock())
    bundle.driver.start.side_effect = RuntimeError("startup failed")
    monkeypatch.setattr(plugin, "get_factory", lambda kind: lambda data: bundle)
    lifecycle = plugin.platform_bundle.__wrapped__({"type": "qbox"})
    with pytest.raises(RuntimeError, match="startup failed"):
        next(lifecycle)
    bundle.driver.stop.assert_called_once()
    bundle.manager.disconnect.assert_called_once()
    bundle.login_primary.assert_not_called()


def test_cleanup_failure_is_not_hidden(monkeypatch):
    bundle = SimpleNamespace(driver=Mock(), manager=Mock(), login_primary=Mock())
    bundle.driver.stop.side_effect = RuntimeError("residual process")
    monkeypatch.setattr(plugin, "get_factory", lambda kind: lambda data: bundle)
    lifecycle = plugin.platform_bundle.__wrapped__({"type": "qbox"})
    assert next(lifecycle) is bundle
    with pytest.raises(RuntimeError, match="residual process"):
        next(lifecycle)
    bundle.manager.disconnect.assert_called_once()


def test_destructive_case_restarts_before_next_case():
    bundle = SimpleNamespace(
        driver=Mock(), manager=Mock(), login_primary=Mock(), _apollo_dirty=False
    )
    request = Mock()
    request.getfixturevalue.return_value = bundle
    request.node.get_closest_marker.side_effect = lambda name: (
        SimpleNamespace(args=()) if name == "destructive" else None
    )
    config = {"image": "bsp"}
    current = plugin._ready_platform.__wrapped__(request, config)
    assert next(current) is bundle
    with pytest.raises(StopIteration):
        next(current)
    assert bundle._apollo_dirty
    bundle.driver.reset.assert_not_called()
    request.node.get_closest_marker.return_value = None
    request.node.get_closest_marker.side_effect = None
    following = plugin._ready_platform.__wrapped__(request, config)
    assert next(following) is bundle
    bundle.driver.reset.assert_called_once()
    bundle.driver.wait_ready.assert_called_once()
    bundle.login_primary.assert_called_once_with(bundle.manager, config)
    assert not bundle._apollo_dirty
    following.close()


def test_failed_phase_attaches_only_current_generation_uart_tail(tmp_path):
    for generation, content in (("run-0001", "stale pass"), ("run-0002", "current failure")):
        directory = tmp_path / "target" / generation
        directory.mkdir(parents=True)
        (directory / "qbox-primary-console.log").write_text(content)
    item = SimpleNamespace(config=SimpleNamespace(_apollo_run_dir=tmp_path))
    report = SimpleNamespace(failed=True, sections=[], when="call")
    hook = plugin.pytest_runtest_makereport(item, None)
    next(hook)
    with pytest.raises(StopIteration):
        hook.send(SimpleNamespace(get_result=lambda: report))
    assert report.sections == [("Captured QBox qbox-primary-console.log call", "current failure")]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, 0, True])
def test_invalid_timeout_is_rejected_before_device_creation(tmp_path, value):
    cfg = SimpleNamespace(get_platform=lambda _: {"image": "bsp", "boot_timeout": value})
    options = {"--platform": "qbox_apollo_qvp", "--build-dir": str(tmp_path),
               "--image": None, "--boot-timeout": None}
    config = SimpleNamespace(getoption=options.get, _apollo_run_dir=tmp_path)
    with pytest.raises(ValueError, match="boot_timeout must be finite and positive"):
        plugin.auto_platform_config_data.__wrapped__(cfg, config)


def test_platform_evidence_does_not_save_ssh_password(tmp_path):
    cfg = SimpleNamespace(get_platform=lambda _: {"image": "bsp", "ssh_password": "test-secret"})
    options = {"--platform": "qbox_apollo_qvp", "--build-dir": str(tmp_path),
               "--image": None, "--boot-timeout": None}
    config = SimpleNamespace(getoption=options.get, _apollo_run_dir=tmp_path)
    data = plugin.auto_platform_config_data.__wrapped__(cfg, config)
    assert data["ssh_password"] == "test-secret"
    assert "test-secret" not in (tmp_path / "platform.json").read_text()


def test_product_network_peer_lives_with_the_device_and_is_closed(tmp_path, monkeypatch):
    bundle = SimpleNamespace(driver=Mock(), manager=Mock(), login_primary=Mock())
    received = {}

    def factory(data):
        received.update(data)
        return bundle

    monkeypatch.setattr(plugin, "get_factory", lambda _: factory)
    lifecycle = plugin.platform_bundle.__wrapped__(
        {"type": "qbox", "image": "product", "log_dir": str(tmp_path)}
    )
    assert next(lifecycle) is bundle
    with urlopen(f"http://127.0.0.1:{received['validation_http_port']}/apollo-qbox-net", timeout=2) as response:
        assert response.read() == b"APOLLO_QBOX_NET_OK"
    lifecycle.close()
    events = [json.loads(line)["event"] for line in (tmp_path / "network-server.jsonl").read_text().splitlines()]
    assert events == ["server-started", "request-served", "server-stopped"]


def test_failed_restart_stops_and_does_not_retry_for_every_case():
    bundle = SimpleNamespace(driver=Mock(), manager=Mock(), login_primary=Mock(), _apollo_dirty=True)
    bundle.driver.wait_ready.side_effect = RuntimeError("boot failed")
    request = Mock()
    request.node.get_closest_marker.return_value = None
    request.getfixturevalue.return_value = bundle
    with pytest.raises(RuntimeError, match="boot failed"):
        next(plugin._ready_platform.__wrapped__(request, {"image": "bsp"}))
    with pytest.raises(RuntimeError, match="restart failed earlier"):
        next(plugin._ready_platform.__wrapped__(request, {"image": "bsp"}))
    bundle.driver.reset.assert_called_once()
    bundle.driver.stop.assert_called_once()
