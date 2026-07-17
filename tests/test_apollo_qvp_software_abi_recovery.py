from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QBOX_PLATFORM = ROOT / "hsoc-stack/tools/qbox-platform"


def read(relative: str) -> str:
    return (QBOX_PLATFORM / relative).read_text(encoding="utf-8")


def test_scmi_malformed_length_releases_channel_with_protocol_error() -> None:
    header = read("systemc-components/mhu320ae/include/mhu320ae.h")
    component_test = read("tests/components/mhu320ae/mhu320ae-tests.cc")

    assert "SCMI_MAX_MESSAGE_LENGTH = 128u" in header
    assert "SCMI_ERR_PROTOCOL = static_cast<uint32_t>(-10)" in header
    assert "length >= sizeof(uint32_t) && length <= capacity" in header
    assert 'trace_event("scmi-malformed-length"' in header
    assert "mem_write32(shmem + SCMI_CHAN_STATUS, SCMI_CHAN_FREE)" in header
    assert "SCMI_PROTOCOL_ERROR" in component_test
    assert "pfdi_shmem.read32(SCMI_STATUS), 1u" in component_test


def test_rpmsg_invalid_descriptor_is_followed_by_valid_retry() -> None:
    component_test = read("tests/components/mhu320ae/mhu320ae-tests.cc")
    invalid = component_test.index("si_cl1_pbx_unused.write16(0x124, 2)")
    retry = component_test.index("si_cl1_pbx_unused.write16(0x124, 0)", invalid)

    assert invalid < retry
    assert "rpmsg-ns-invalid-desc" in read(
        "systemc-components/mhu320ae/include/mhu320ae.h"
    )
    assert "rpmsg-ns-poll-timeout" in read(
        "systemc-components/mhu320ae/include/mhu320ae.h"
    )


def test_apollo_software_contract_records_cleanup_and_recovery() -> None:
    contract = read("platforms/apollo/hw-block/software_contract.lua")

    assert 'malformed_request = "protocol_error"' in contract
    assert 'recovery = "channel_free_next_request"' in contract
    assert 'malformed_descriptor = "bounded_poll_timeout"' in contract
    assert 'recovery = "next_doorbell_retry"' in contract
