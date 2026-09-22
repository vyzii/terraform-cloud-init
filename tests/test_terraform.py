import pytest

from terraform_cloud_init.terraform import build_backend_config_arg, build_init_command
from terraform_cloud_init.validation import ConfigError


class TestBuildBackendConfigArg:
    @pytest.mark.parametrize("provider", ["aws", "azure"])
    def test_key_style_backends(self, provider):
        arg = build_backend_config_arg(provider, "myrepo/dev-network")
        assert arg == "key=myrepo/dev-network/default.tfstate"

    def test_gcp_uses_prefix_without_filename(self):
        arg = build_backend_config_arg("gcp", "myrepo/dev-network")
        assert arg == "prefix=myrepo/dev-network"

    @pytest.mark.parametrize("path", ["/myrepo/dev/", "myrepo/dev/", "/myrepo/dev"])
    def test_surrounding_slashes_are_stripped(self, path):
        assert build_backend_config_arg("aws", path) == "key=myrepo/dev/default.tfstate"
        assert build_backend_config_arg("gcp", path) == "prefix=myrepo/dev"


class TestBuildInitCommand:
    def test_backend_disabled(self, make_config):
        cmd = build_init_command(make_config(init_backend=False))

        assert cmd == ["terraform", "init", "-input=false", "-backend=false"]

    def test_backend_disabled_ignores_missing_inputs(self, make_config):
        # No provider or path set: still fine when the backend is skipped.
        cmd = build_init_command(make_config(init_backend=False))

        assert not any(part.startswith("-backend-config") for part in cmd)

    def test_aws(self, valid_config):
        cmd = build_init_command(valid_config("aws"))

        assert cmd == [
            "terraform",
            "init",
            "-input=false",
            "-backend-config=key=myrepo/dev-network/default.tfstate",
        ]

    def test_azure(self, valid_config):
        cmd = build_init_command(valid_config("azure"))

        assert "-backend-config=key=myrepo/dev-network/default.tfstate" in cmd

    def test_gcp(self, valid_config):
        cmd = build_init_command(valid_config("gcp"))

        assert "-backend-config=prefix=myrepo/dev-network" in cmd

    def test_backend_enabled_does_not_disable_backend(self, valid_config):
        assert "-backend=false" not in build_init_command(valid_config("aws"))

    def test_invalid_config_raises_with_all_errors(self, valid_config):
        cfg = valid_config("azure", azure_tenant_id=None, backend_path=None)

        with pytest.raises(ConfigError) as exc_info:
            build_init_command(cfg)

        assert len(exc_info.value.errors) == 2

    def test_unknown_provider_raises(self, make_config):
        cfg = make_config(backend_provider="azrue", backend_path="myrepo/dev")

        with pytest.raises(ConfigError):
            build_init_command(cfg)
