import pytest

pytestmark = [pytest.mark.domain('si_cl1'), pytest.mark.category('network'), pytest.mark.image("any")]


@pytest.mark.skip(reason='hipc: QBox bidirectional ICMP/TCP/UDP and boundary/multistream tests are not implemented')
def test_hipc_bidirectional_transport_and_boundaries():
    pass
