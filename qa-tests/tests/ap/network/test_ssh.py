import pytest

pytestmark = [pytest.mark.image("any"), pytest.mark.domain("ap"), pytest.mark.category("network")]


def test_primary_ssh_executes_guest_command(platform_base_obj):
    manager = platform_base_obj.mgr
    port = manager.get_port("ssh")
    rc, output = manager.execute_command_with_prompt_capture(
        port, "printf 'APOLLO_SSH_OK\\n'; uname -s; uname -m; id -u", timeout=60,
    )
    assert rc == 0, f"SSH guest command failed (rc={rc}): {output}"
    assert output.splitlines() == ["APOLLO_SSH_OK", "Linux", "aarch64", "0"]
