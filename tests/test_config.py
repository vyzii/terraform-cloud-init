import pytest

from terraform_cloud_init.config import get_bool_input, get_input, load_config

ENV_VARS = [
    "INIT_BACKEND",
    "BACKEND_PROVIDER",
    "BACKEND_PATH",
    "AWS_REGION",
    "AWS_ROLE_ARN",
    "AZURE_CLIENT_ID",
    "AZURE_TENANT_ID",
    "AZURE_SUBSCRIPTION_ID",
    "GCP_WORKLOAD_IDENTITY_PROVIDER",
    "GCP_SERVICE_ACCOUNT",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


class TestGetInput:
    def test_unset_returns_none(self):
        assert get_input("BACKEND_PATH") is None

    def test_empty_returns_none(self, monkeypatch):
        monkeypatch.setenv("BACKEND_PATH", "")
        assert get_input("BACKEND_PATH") is None

    def test_whitespace_only_returns_none(self, monkeypatch):
        monkeypatch.setenv("BACKEND_PATH", "   ")
        assert get_input("BACKEND_PATH") is None

    def test_value_is_trimmed(self, monkeypatch):
        monkeypatch.setenv("BACKEND_PATH", "  prod/network  ")
        assert get_input("BACKEND_PATH") == "prod/network"


class TestGetBoolInput:
    @pytest.mark.parametrize("default", [True, False])
    def test_unset_uses_default(self, default):
        assert get_bool_input("INIT_BACKEND", default=default) is default

    def test_empty_uses_default(self, monkeypatch):
        monkeypatch.setenv("INIT_BACKEND", "")
        assert get_bool_input("INIT_BACKEND", default=True) is True

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("true", True),
            ("false", False),
            ("TRUE", True),
            ("False", False),
            ("  true  ", True),
        ],
    )
    def test_parses_values(self, monkeypatch, raw, expected):
        monkeypatch.setenv("INIT_BACKEND", raw)
        assert get_bool_input("INIT_BACKEND", default=True) is expected

    @pytest.mark.parametrize("raw", ["yes", "1", "flase", "no"])
    def test_invalid_value_exits_with_annotation(self, monkeypatch, capsys, raw):
        monkeypatch.setenv("INIT_BACKEND", raw)

        with pytest.raises(SystemExit) as exc_info:
            get_bool_input("INIT_BACKEND", default=True)

        assert exc_info.value.code == 1
        assert "::error::" in capsys.readouterr().out


class TestLoadConfig:
    def test_defaults_when_nothing_set(self):
        cfg = load_config()

        assert cfg.init_backend is True
        assert cfg.backend_provider is None
        assert cfg.backend_path is None

    def test_reads_all_fields(self, monkeypatch):
        monkeypatch.setenv("INIT_BACKEND", "false")
        monkeypatch.setenv("BACKEND_PROVIDER", "azure")
        monkeypatch.setenv("BACKEND_PATH", "myrepo/dev-network")
        monkeypatch.setenv("AWS_REGION", "us-east-1")
        monkeypatch.setenv("AWS_ROLE_ARN", "arn:aws:iam::123456789012:role/tf")
        monkeypatch.setenv("AZURE_CLIENT_ID", "client")
        monkeypatch.setenv("AZURE_TENANT_ID", "tenant")
        monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "subscription")
        monkeypatch.setenv("GCP_WORKLOAD_IDENTITY_PROVIDER", "wip")
        monkeypatch.setenv("GCP_SERVICE_ACCOUNT", "sa@example.com")

        cfg = load_config()

        assert cfg.init_backend is False
        assert cfg.backend_provider == "azure"
        assert cfg.backend_path == "myrepo/dev-network"
        assert cfg.aws_region == "us-east-1"
        assert cfg.aws_role_arn == "arn:aws:iam::123456789012:role/tf"
        assert cfg.azure_client_id == "client"
        assert cfg.azure_tenant_id == "tenant"
        assert cfg.azure_subscription_id == "subscription"
        assert cfg.gcp_workload_identity_provider == "wip"
        assert cfg.gcp_service_account == "sa@example.com"

    def test_empty_inputs_become_none(self, monkeypatch):
        monkeypatch.setenv("BACKEND_PROVIDER", "")
        assert load_config().backend_provider is None
