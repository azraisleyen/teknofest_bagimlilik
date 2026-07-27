import tomllib
from importlib.resources import files
from pathlib import Path


def test_package_discovery_is_explicit_and_limited() -> None:
    configuration = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    discovery = configuration["tool"]["setuptools"]["packages"]["find"]

    assert discovery["where"] == [".", "clients/python"]
    assert discovery["include"] == ["apps*", "config*", "sentra_qr_client*"]
    assert "tests*" in discovery["exclude"]
    assert discovery["namespaces"] is False


def test_contract_schemas_are_package_resources() -> None:
    schema_root = files("apps.qr.schemas.v1")
    assert schema_root.joinpath("content-started.schema.json").is_file()
    assert schema_root.joinpath("content-ended.schema.json").is_file()


def test_packaged_schemas_match_public_contracts() -> None:
    for filename in ("content-started.schema.json", "content-ended.schema.json"):
        packaged = files("apps.qr.schemas.v1").joinpath(filename).read_bytes()
        public = Path("contracts/v1", filename).read_bytes()
        assert packaged == public
