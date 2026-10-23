import pytest

pytestmark = [pytest.mark.domain('ap'), pytest.mark.category('power'), pytest.mark.image("any")]


@pytest.mark.skip(reason='mbpp: isolated 16-CPU artifacts and the QBox MBPP probe are not implemented')
def test_mbpp_cpu_parking_profiles():
    pass
