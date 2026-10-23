import pytest

from test_automation.checks.profiles import execute_profile

pytestmark = [pytest.mark.domain('ap'), pytest.mark.category('security'), pytest.mark.image("product-only")]


def test_psa_crypto_storage_and_attestation(platform_base_obj, record_property):
    execute_profile(platform_base_obj, 'trusted-services', record_property)
