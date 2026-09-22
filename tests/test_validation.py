import pytest

from terraform_cloud_init.validation import REQUIRED, ConfigError, validate


class TestValidate:
    def test_backend_disabled_needs_nothing(self, make_config):
        cfg = make_config(init_backend=False)
        assert validate(cfg) == []

    @pytest.mark.parametrize("provider", ["aws", "azure", "gcp"])
    def test_fully_populated_provider_is_valid(self, valid_config, provider):
        assert validate(valid_config(provider)) == []

    @pytest.mark.parametrize("provider", [None, "azrue", "AWS", ""])
    def test_unknown_or_missing_provider(self, make_config, provider):
        cfg = make_config(backend_provider=provider, backend_path="myrepo/dev")

        errors = validate(cfg)

        assert len(errors) == 1
        assert "backend-provider must be one of" in errors[0]

    def test_unknown_provider_error_lists_valid_options(self, make_config):
        errors = validate(make_config(backend_provider="nope"))

        for provider in REQUIRED:
            assert provider in errors[0]

    @pytest.mark.parametrize(
        "provider, missing_field, input_name",
        [
            ("aws", "aws_region", "aws-region"),
            ("aws", "aws_role_arn", "aws-role-arn"),
            ("aws", "backend_path", "backend-path"),
            ("azure", "azure_client_id", "azure-client-id"),
            ("azure", "azure_tenant_id", "azure-tenant-id"),
            ("azure", "azure_subscription_id", "azure-subscription-id"),
            ("azure", "backend_path", "backend-path"),
            ("gcp", "gcp_workload_identity_provider", "gcp-workload-identity-provider"),
            ("gcp", "gcp_service_account", "gcp-service-account"),
            ("gcp", "backend_path", "backend-path"),
        ],
    )
    def test_single_missing_input(
        self, valid_config, provider, missing_field, input_name
    ):
        cfg = valid_config(provider, **{missing_field: None})

        assert validate(cfg) == [f"missing required input for {provider}: {input_name}"]

    def test_reports_every_missing_input_at_once(self, valid_config):
        cfg = valid_config("azure", azure_tenant_id=None, backend_path=None)

        errors = validate(cfg)

        assert len(errors) == 2
        assert any("azure-tenant-id" in error for error in errors)
        assert any("backend-path" in error for error in errors)

    def test_other_providers_inputs_are_ignored(self, valid_config):
        cfg = valid_config("aws", azure_client_id="unused")
        assert validate(cfg) == []

    def test_required_fields_exist_on_config(self, make_config):
        """Guards against renaming a Config field without updating REQUIRED."""
        cfg = make_config()

        for provider, fields in REQUIRED.items():
            for field_name in fields:
                assert hasattr(cfg, field_name), f"{provider}: {field_name}"


class TestConfigError:
    def test_keeps_every_error(self):
        error = ConfigError(["first", "second"])

        assert error.errors == ["first", "second"]

    def test_message_joins_errors(self):
        assert str(ConfigError(["first", "second"])) == "first; second"
