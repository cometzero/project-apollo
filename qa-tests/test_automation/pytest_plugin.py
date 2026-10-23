"""Guide-compatible pytest fixtures and Apollo runtime lifecycle."""

from datetime import datetime, timezone
from contextlib import ExitStack
from pathlib import Path
import json
import math
import tempfile

import pytest

from test_automation.configs.config import Config
from test_automation.targets.registry import get_factory
from test_automation.utils.auto_platform_base import AutoTestPlatformBase
from apollo_validation.qbox_network import platform_network_server

QA_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = QA_ROOT.parent
IMAGE_SCOPES = ("bsp-only", "product-only", "any")


def pytest_addoption(parser):
    group = parser.getgroup("Apollo runtime")
    group.addoption("--platform", default="qbox_apollo_qvp")
    group.addoption("--config", default=str(QA_ROOT / "configs/qbox.yaml"))
    group.addoption("--build-dir", default=str(WORKSPACE / "build"))
    group.addoption("--image", choices=("bsp", "product"), default=None)
    group.addoption("--test-scope", choices=IMAGE_SCOPES,
                    help="Select exactly one test applicability group; --image selects the boot image")
    group.addoption("--boot-timeout", type=float, default=None)
    group.addoption("--run-dir", help="New directory for reports and DUT logs")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    from test_automation import reporting

    requested = config.getoption("--run-dir")
    if requested:
        run_dir = Path(requested).expanduser().resolve()
        run_dir.mkdir(parents=True, exist_ok=False)
    else:
        root = WORKSPACE / "build/qbox-apollo-qvp"
        root.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = Path(tempfile.mkdtemp(prefix=f"qa-runtime-{stamp}-", dir=root))
    config._apollo_run_dir = run_dir
    if not config.option.xmlpath:
        config.option.xmlpath = str(run_dir / "junit.xml")
    reporting.configure(config)
    (run_dir / "invocation.json").write_text(json.dumps({
        "argv": list(config.invocation_params.args),
        "cwd": str(config.invocation_params.dir),
        "platform": config.getoption("--platform"),
        "config": config.getoption("--config"),
        "build_dir": config.getoption("--build-dir"),
        "image_override": config.getoption("--image"),
    }, indent=2) + "\n", encoding="utf-8")


def get_image_scope(item):
    marker = item.get_closest_marker("image")
    if marker is None:
        return "any"
    if len(marker.args) != 1 or marker.kwargs or marker.args[0] not in IMAGE_SCOPES:
        message = f"{item.nodeid}: image marker must be one of {IMAGE_SCOPES}"
        item.config.hook.pytest_collectreport(report=pytest.CollectReport(
            nodeid=item.nodeid, outcome="failed", longrepr=message, result=[]
        ))
        raise pytest.UsageError(message)
    return marker.args[0]


def pytest_collection_modifyitems(config, items):
    selected, deselected = [], []
    requested = config.getoption("--test-scope")
    image = config.getoption("--image")
    if image is None:
        settings = Config(path=str(Path(config.getoption("--config")).expanduser()),
                          build_dir=config.getoption("--build-dir"))
        image = settings.get_platform(config.getoption("--platform"))["image"]
    if image not in ("bsp", "product"):
        raise pytest.UsageError("QBox image must be bsp or product")
    for item in items:
        scope = get_image_scope(item)
        item.user_properties.append(("image_scope", scope))
        if scope != "any" and scope != f"{image}-only":
            item.add_marker(pytest.mark.skip(reason=(
                f"{scope}: requires --image={scope.removesuffix('-only')}; selected --image={image}"
            )))
        (selected if requested is None or scope == requested else deselected).append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
    # Capture initial boot evidence before hotplug and fault-injection cases.
    items[:] = sorted(selected, key=lambda item: item.path.parent.name != "boot")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if not report.failed:
        return
    generations = sorted((item.config._apollo_run_dir / "target").glob("run-*"))
    if not generations:
        return
    for path in sorted(generations[-1].glob("qbox-*.log")):
        with path.open("rb") as stream:
            stream.seek(0, 2)
            stream.seek(max(0, stream.tell() - 8192))
            tail = stream.read().decode("utf-8", errors="replace")
        report.sections.append((f"Captured QBox {path.name} {report.when}", tail))


@pytest.fixture(scope="session")
def cfg(pytestconfig):
    return Config(
        path=str(Path(pytestconfig.getoption("--config")).expanduser()),
        build_dir=pytestconfig.getoption("--build-dir"),
    )


@pytest.fixture(scope="session")
def auto_platform_config_data(cfg, pytestconfig):
    data = dict(cfg.get_platform(pytestconfig.getoption("--platform")))
    data.setdefault("workspace_root", str(WORKSPACE))
    data["build_dir"] = str(Path(pytestconfig.getoption("--build-dir")).expanduser().resolve())
    data["log_dir"] = str(pytestconfig._apollo_run_dir / "target")
    for key in ("image", "boot_timeout"):
        value = pytestconfig.getoption("--" + key.replace("_", "-"))
        if value is not None:
            data[key] = value
    if data.get("image") not in ("bsp", "product"):
        raise ValueError("QBox image must be bsp or product")
    for key in ("boot_timeout", "command_timeout", "run_timeout"):
        if key in data and (isinstance(data[key], bool)
                            or not math.isfinite(float(data[key])) or float(data[key]) <= 0):
            raise ValueError(f"{key} must be finite and positive")
    (pytestconfig._apollo_run_dir / "platform.json").write_text(
        json.dumps({key: value for key, value in data.items() if key != "ssh_password"}, indent=2)
        + "\n", encoding="utf-8"
    )
    return data


@pytest.fixture(scope="session")
def platform_bundle(auto_platform_config_data):
    from test_automation.targets.qbox import plugin  # noqa: F401

    data = dict(auto_platform_config_data)
    factory = get_factory(data["type"])
    if factory is None:
        raise ValueError(f"Unregistered target type: {data['type']}")
    with ExitStack() as resources:
        if data.get("image") == "product":
            network = resources.enter_context(platform_network_server(
                Path(data["log_dir"]) / "network-server.jsonl"
            ))
            data["validation_http_port"] = network.host_port
        bundle = factory(data)
        bundle._apollo_dirty = False
        try:
            bundle.driver.init()
            bundle.driver.start()
            bundle.driver.wait_ready()
            if bundle.login_primary:
                bundle.login_primary(bundle.manager, data)
            yield bundle
        finally:
            try:
                bundle.driver.stop()
            finally:
                if bundle.manager:
                    bundle.manager.disconnect()


@pytest.fixture
def _ready_platform(request, auto_platform_config_data):
    bundle = request.getfixturevalue("platform_bundle")
    if getattr(bundle, "_apollo_start_error", None) is not None:
        raise RuntimeError("QBox restart failed earlier in this session") from bundle._apollo_start_error
    if bundle._apollo_dirty:
        try:
            bundle.driver.reset()
            bundle.driver.wait_ready()
            if bundle.login_primary:
                bundle.login_primary(bundle.manager, auto_platform_config_data)
        except Exception as error:
            bundle._apollo_start_error = error
            bundle.driver.stop()
            raise
        bundle._apollo_dirty = False
    try:
        yield bundle
    finally:
        if request.node.get_closest_marker("destructive"):
            bundle._apollo_dirty = True


@pytest.fixture
def platform_driver(_ready_platform):
    return _ready_platform.driver


@pytest.fixture
def session_manager(_ready_platform):
    return _ready_platform.manager


@pytest.fixture
def platform_base_obj(session_manager, auto_platform_config_data, pytestconfig):
    return AutoTestPlatformBase(
        session_manager, auto_platform_config_data, pytestconfig.getoption("--platform")
    )


@pytest.fixture(scope="session")
def platform_name(pytestconfig):
    return pytestconfig.getoption("--platform")
