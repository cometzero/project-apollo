import pytest

pytestmark = [pytest.mark.domain('ap'), pytest.mark.category('security'), pytest.mark.image("any")]


@pytest.mark.skip(reason='crypto-extension: QBox instruction/workload validation is not implemented; FVP plugin wall-time results are not QBox evidence')
def test_crypto_extension_instruction_and_workload_coverage():
    pass
