from importlib.metadata import version

import pv


def test_version_matches_package_metadata() -> None:
    assert pv.__version__ == version("policyvalue-ca")
